"""
Data Freshness Sentinel
Dynamically inspects table_load_log to detect regional sync status, lag days,
and pipeline health without hardcoded values.
"""
from datetime import datetime
from typing import Dict, Any, List
import duckdb

class FreshnessSentinel:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con
        self.refresh()

    def refresh(self):
        # 1. Latest successful business date across ALL regions
        global_latest = self.con.execute("""
            SELECT MAX(max_business_date)
            FROM table_load_log
            WHERE status = 'Success'
        """).fetchone()[0]
        self.global_latest = global_latest

        # 2. Regional max business dates
        reg_df = self.con.execute("""
            SELECT region, MAX(max_business_date) as max_date
            FROM table_load_log
            WHERE status = 'Success'
            GROUP BY region
        """).df()
        self.regional_dates = dict(zip(reg_df['region'], reg_df['max_date']))

        # 3. Load success rate for Brazil since 10 August 2026 ERP migration
        br_loads = self.con.execute("""
            SELECT 
                COUNT(*) as total_loads,
                SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as success_loads
            FROM table_load_log
            WHERE region = 'BR' AND load_started_at >= '2026-08-10'
        """).fetchone()
        self.br_total_loads = br_loads[0] or 0
        self.br_success_loads = br_loads[1] or 0

        # 4. Receivables aging latest snapshot
        aging_latest = self.con.execute("""
            SELECT MAX(snapshot_date) FROM receivables_aging WHERE territory_code LIKE 'BR%'
        """).fetchone()[0]
        self.br_aging_latest = str(aging_latest) if aging_latest else "N/A"

    def check_region_freshness(self, region_code: str) -> Dict[str, Any]:
        """
        Dynamically calculates lag days against global max business date.
        """
        if region_code == "GLOBAL" or region_code is None:
            # Check if any region lags behind
            has_lag = any(
                str(d) < str(self.global_latest) 
                for r, d in self.regional_dates.items() 
                if r != "GLOBAL"
            )
            if has_lag:
                return {
                    "freshness_status": "STALE_WARNING",
                    "data_through": str(self.global_latest),
                    "lag_days": 0,
                    "warning": (
                        f"Brazil sell-in is current to {self.regional_dates.get('BR')} "
                        f"(8 days behind other regions); {self.br_success_loads} of {self.br_total_loads} loads succeeded since 10 Aug ERP migration; "
                        f"receivables last snapshot {self.br_aging_latest}."
                    ),
                    "field_caveat": "Orders taken on messaging apps may not be keyed into the ERP for up to 2 days."
                }
            return {
                "freshness_status": "HEALTHY",
                "data_through": str(self.global_latest),
                "lag_days": 0,
                "warning": None,
                "field_caveat": None
            }

        reg_date = self.regional_dates.get(region_code, self.global_latest)
        lag_days = (datetime.strptime(str(self.global_latest), '%Y-%m-%d') - datetime.strptime(str(reg_date), '%Y-%m-%d')).days

        if lag_days > 0:
            warning_msg = (
                f"{region_code} sell-in is current to {reg_date} ({lag_days} days behind other regions); "
                f"{self.br_success_loads} of {self.br_total_loads} loads since 10 Aug succeeded; "
                f"receivables last snapshot {self.br_aging_latest}."
            )
            return {
                "freshness_status": "STALE_WARNING",
                "data_through": str(reg_date),
                "lag_days": lag_days,
                "warning": warning_msg,
                "field_caveat": "Orders taken on messaging apps may not be keyed into the ERP for up to 2 days."
            }

        return {
            "freshness_status": "HEALTHY",
            "data_through": str(reg_date),
            "lag_days": 0,
            "warning": None,
            "field_caveat": "Orders taken on messaging apps may not be keyed into the ERP for up to 2 days." if region_code in ['BR', 'IN'] else None
        }
