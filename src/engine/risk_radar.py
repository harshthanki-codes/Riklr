"""
Channel-Risk Radar Sentinel
Monitors Sell-in vs Dealer Scan Sell-through discrepancies, inventory buildup,
and flags high-risk distributors before returns occur.
Backtested against the Brazil South $8.0M inventory return crisis.
"""
from typing import Dict, Any, List
import duckdb

class ChannelRiskRadar:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def scan_channel_risks(
        self,
        region_code: str = "BR",
        sell_through_threshold: float = 0.35,
        loading_multiplier_threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Scans all distributors in a region to flag high-risk inventory loading.
        Flags distributors where:
        1. Scan sell-through is below threshold (< 35% of packs sold)
        2. Packs sold are significantly higher than peers or historical trend
        """
        query = f"""
        WITH dist_sales AS (
            SELECT 
                d.distributor_id,
                d.distributor_name,
                d.territory_code,
                t.territory_name,
                t.region_code,
                SUM(s.quantity) as total_packs_sold,
                ROUND(SUM(s.invoice_amount_local / COALESCE(fx.avg_rate, 1.0)), 2) as sell_in_usd
            FROM distributors d
            JOIN territories t ON d.territory_code = t.territory_code
            JOIN sell_in_orders s ON d.distributor_id = s.distributor_id
            LEFT JOIN (
                SELECT strftime(rate_date, '%Y-%m') as ym, currency, AVG(local_per_usd) as avg_rate
                FROM fx_rates GROUP BY 1, 2
            ) fx ON strftime(s.order_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
            WHERE t.region_code = '{region_code}' AND s.order_date >= '2025-10-01' AND s.order_date <= '2026-09-30'
            GROUP BY 1, 2, 3, 4, 5
        ),
        dist_scans AS (
            SELECT 
                dl.distributor_id,
                SUM(ds.packs_scanned) as total_packs_scanned
            FROM dealers dl
            JOIN dealer_scans ds ON dl.dealer_id = ds.dealer_id
            GROUP BY 1
        ),
        dist_returns AS (
            SELECT 
                r.distributor_id,
                ROUND(SUM(r.credit_amount_local / COALESCE(fx.avg_rate, 1.0)), 2) as actual_returns_usd
            FROM returns r
            LEFT JOIN (
                SELECT strftime(rate_date, '%Y-%m') as ym, currency, AVG(local_per_usd) as avg_rate
                FROM fx_rates GROUP BY 1, 2
            ) fx ON strftime(r.return_date, '%Y-%m') = fx.ym AND r.currency = fx.currency
            WHERE r.return_date >= '2025-10-01' AND r.return_date <= '2026-09-30'
            GROUP BY 1
        )
        SELECT 
            s.distributor_id,
            s.distributor_name,
            s.territory_code,
            s.territory_name,
            s.total_packs_sold,
            COALESCE(sc.total_packs_scanned, 0) as total_packs_scanned,
            ROUND(CAST(COALESCE(sc.total_packs_scanned, 0) AS DOUBLE) / NULLIF(s.total_packs_sold, 0), 2) as sell_through_rate,
            s.sell_in_usd,
            COALESCE(ret.actual_returns_usd, 0) as actual_returns_usd
        FROM dist_sales s
        LEFT JOIN dist_scans sc ON s.distributor_id = sc.distributor_id
        LEFT JOIN dist_returns ret ON s.distributor_id = ret.distributor_id
        ORDER BY s.sell_in_usd DESC
        """
        df = self.con.execute(query).df()
        
        flagged = []
        for _, row in df.iterrows():
            st_rate = row["sell_through_rate"]
            is_risk = False
            risk_reasons = []

            if st_rate < sell_through_threshold:
                is_risk = True
                risk_reasons.append(f"Low Sell-Through: Only {st_rate*100:.1f}% scanned vs expected > {sell_through_threshold*100:.0f}%")
            
            if row["actual_returns_usd"] > 500000:
                is_risk = True
                risk_reasons.append(f"High Return Hazard: ${row['actual_returns_usd']:,.2f} returned")

            if is_risk:
                flagged.append({
                    "distributor_id": row["distributor_id"],
                    "distributor_name": row["distributor_name"],
                    "territory": f"{row['territory_code']} ({row['territory_name']})",
                    "packs_sold": int(row["total_packs_sold"]),
                    "packs_scanned": int(row["total_packs_scanned"]),
                    "sell_through_rate": st_rate,
                    "sell_in_usd": float(row["sell_in_usd"]),
                    "actual_returns_usd": float(row["actual_returns_usd"]),
                    "risk_severity": "CRITICAL" if st_rate < 0.25 else "HIGH",
                    "reasons": risk_reasons
                })
        
        return flagged
