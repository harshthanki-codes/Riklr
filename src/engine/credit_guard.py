"""
Credit Exposure & Working Capital Guard Engine
Identifies distributors with extreme credit limit utilization (>100%),
measures collateral risk, and isolates credit committee review triggers (90+ day overdues).
"""
from typing import Dict, Any, List
import duckdb

class CreditExposureGuard:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def get_overdraft_breaches(
        self,
        snapshot_date: str = "2026-08-31",
        utilization_threshold: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Flags distributors whose total outstanding exceeds credit limit.
        """
        query = f"""
        SELECT 
            r.distributor_id,
            d.distributor_name,
            d.territory_code,
            t.region_code,
            d.currency,
            d.credit_limit_local,
            r.total_outstanding_local,
            r.not_due_local,
            r.overdue_90_plus_local,
            r.disputed_local,
            ROUND((r.total_outstanding_local - d.credit_limit_local), 2) as overdraft_amount,
            ROUND(r.total_outstanding_local * 100.0 / NULLIF(d.credit_limit_local, 0), 1) as utilization_pct
        FROM receivables_aging r
        JOIN distributors d ON r.distributor_id = d.distributor_id
        JOIN territories t ON d.territory_code = t.territory_code
        WHERE r.snapshot_date = '{snapshot_date}'
          AND r.total_outstanding_local > d.credit_limit_local
        ORDER BY overdraft_amount DESC;
        """
        df = self.con.execute(query).df()
        
        breaches = []
        for _, row in df.iterrows():
            util = row["utilization_pct"]
            breaches.append({
                "distributor_id": row["distributor_id"],
                "distributor_name": row["distributor_name"],
                "territory": row["territory_code"],
                "region": row["region_code"],
                "currency": row["currency"],
                "credit_limit": float(row["credit_limit_local"]),
                "outstanding": float(row["total_outstanding_local"]),
                "overdraft": float(row["overdraft_amount"]),
                "utilization_pct": util,
                "overdue_90_plus": float(row["overdue_90_plus_local"]),
                "disputed": float(row["disputed_local"]),
                "severity": "CRITICAL" if util > 300.0 else ("HIGH" if util > 150.0 else "ELEVATED")
            })
            
        return breaches
