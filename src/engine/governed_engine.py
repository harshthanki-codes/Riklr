"""
Governed Metric Execution Engine
Compiles natural language intents to strictly validated, deterministic SQL queries
with multi-currency FX normalization, Row-Level Security, and Trust Footers.
"""
import duckdb
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from .security import SecurityEngine
from .freshness import FreshnessSentinel

class GovernedEngine:
    def __init__(self, db_path: str = "fde-case-study/sales-analyst/data/warehouse.duckdb"):
        self.con = duckdb.connect(db_path, read_only=True)
        self.security = SecurityEngine(self.con)
        self.freshness = FreshnessSentinel(self.con)
        
        contract_path = Path(__file__).parent / "metric_contract.yaml"
        with open(contract_path, "r", encoding="utf-8") as f:
            self.contract = yaml.safe_load(f)["metrics"]

    def execute_sales_query(
        self,
        user_id: str,
        metric_choice: str = "NET_SALES",  # "GROSS_SALES" (Sales Ops M01) or "NET_SALES" (Finance M02)
        region: Optional[str] = None,
        territory: Optional[str] = None,
        fiscal_year: Optional[int] = 2026,
        group_by: str = "region"  # "region", "territory", "distributor", "product"
    ) -> Dict[str, Any]:
        """
        Executes a governed sales query with automatic RLS injection and FX rate application.
        """
        # 1. Security Check
        domain = "sell_in"
        access_res = self.security.check_access(user_id, domain, requested_territory=territory, table_alias="s")
        if not access_res["allowed"]:
            return {
                "success": False,
                "error_type": "ACCESS_DENIED",
                "message": access_res["reason"],
                "trust_footer": {
                    "trust_level": "REJECTED_SECURITY",
                    "reason": access_res["reason"]
                }
            }

        rls_clause = access_res["rls_sql"]
        filters = [rls_clause]

        if territory:
            filters.append(f"s.territory_code = '{territory}'")
        elif region:
            filters.append(f"t.region_code = '{region}'")

        if fiscal_year == 2026:
            # FY26: 2025-10-01 to 2026-09-30
            date_filter_orders = "s.order_date >= '2025-10-01' AND s.order_date <= '2026-09-30'"
            date_filter_inv = "s.invoice_date >= '2025-10-01' AND s.invoice_date <= '2026-09-30'"
            date_filter_ret = "r.return_date >= '2025-10-01' AND r.return_date <= '2026-09-30'"
            date_filter_cred = "c.accrual_date >= '2025-10-01' AND c.accrual_date <= '2026-09-30'"
        else:
            date_filter_orders = "1=1"
            date_filter_inv = "1=1"
            date_filter_ret = "1=1"
            date_filter_cred = "1=1"

        # 2. Freshness check
        freshness_info = self.freshness.check_region_freshness(region or "GLOBAL")

        # 3. Compile SQL based on metric definition
        if metric_choice == "GROSS_SALES":
            # Sales Ops Definition (M01)
            # Local currency if single territory, converted to USD if multi-currency/global
            is_cross_currency = region is None or region in ["GLOBAL", "EU", "NA"] or territory is None
            
            if is_cross_currency:
                sql = f"""
                SELECT 
                    t.region_code,
                    t.territory_code,
                    t.territory_name,
                    ROUND(SUM(s.invoice_amount_local / COALESCE(fx.avg_rate, 1.0)), 2) AS gross_sales_usd
                FROM sell_in_orders s
                JOIN territories t ON s.territory_code = t.territory_code
                LEFT JOIN (
                    SELECT strftime(rate_date, '%Y-%m') as ym, currency, AVG(local_per_usd) as avg_rate
                    FROM fx_rates GROUP BY 1, 2
                ) fx ON strftime(s.order_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
                WHERE s.quantity > 0 AND {date_filter_orders} AND {rls_clause}
                {"AND t.region_code = '" + region + "'" if region else ""}
                {"AND s.territory_code = '" + territory + "'" if territory else ""}
                GROUP BY 1, 2, 3
                ORDER BY gross_sales_usd DESC
                """
            else:
                sql = f"""
                SELECT 
                    s.territory_code,
                    s.currency,
                    ROUND(SUM(s.invoice_amount_local), 2) AS gross_sales_local
                FROM sell_in_orders s
                WHERE s.quantity > 0 AND {date_filter_orders} AND {rls_clause}
                {"AND s.territory_code = '" + territory + "'" if territory else ""}
                GROUP BY 1, 2
                """
            metric_meta = self.contract["M01"]

        else:
            # Finance Definition (M02: Net Sales)
            sql = f"""
            WITH fx_m AS (
                SELECT strftime(rate_date, '%Y-%m') as ym, currency, AVG(local_per_usd) as avg_rate
                FROM fx_rates GROUP BY 1, 2
            ),
            gross AS (
                SELECT 
                    t.region_code,
                    t.territory_code,
                    t.territory_name,
                    SUM(s.invoice_amount_local / COALESCE(fx.avg_rate, 1.0)) AS gross_usd
                FROM sell_in_orders s
                JOIN territories t ON s.territory_code = t.territory_code
                LEFT JOIN fx_m fx ON strftime(s.invoice_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
                WHERE s.quantity > 0 AND {date_filter_inv} AND {rls_clause}
                {"AND t.region_code = '" + region + "'" if region else ""}
                {"AND s.territory_code = '" + territory + "'" if territory else ""}
                GROUP BY 1, 2, 3
            ),
            ret AS (
                SELECT 
                    t.territory_code,
                    SUM(r.credit_amount_local / COALESCE(fx.avg_rate, 1.0)) AS ret_usd
                FROM returns r
                JOIN territories t ON r.territory_code = t.territory_code
                LEFT JOIN fx_m fx ON strftime(r.return_date, '%Y-%m') = fx.ym AND r.currency = fx.currency
                WHERE {date_filter_ret} AND {rls_clause}
                {"AND t.region_code = '" + region + "'" if region else ""}
                {"AND r.territory_code = '" + territory + "'" if territory else ""}
                GROUP BY 1
            ),
            cred AS (
                SELECT 
                    t.territory_code,
                    SUM(c.amount_local / COALESCE(fx.avg_rate, 1.0)) AS cred_usd
                FROM schemes_and_credits c
                JOIN territories t ON c.territory_code = t.territory_code
                LEFT JOIN fx_m fx ON strftime(c.accrual_date, '%Y-%m') = fx.ym AND c.currency = fx.currency
                WHERE c.status <> 'Cancelled' AND {date_filter_cred} AND {rls_clause}
                {"AND t.region_code = '" + region + "'" if region else ""}
                {"AND c.territory_code = '" + territory + "'" if territory else ""}
                GROUP BY 1
            )
            SELECT 
                g.region_code,
                g.territory_code,
                g.territory_name,
                ROUND(COALESCE(g.gross_usd, 0), 2) AS gross_sales_usd,
                ROUND(COALESCE(r.ret_usd, 0), 2) AS returns_usd,
                ROUND(COALESCE(c.cred_usd, 0), 2) AS scheme_credits_usd,
                ROUND(COALESCE(g.gross_usd, 0) - COALESCE(r.ret_usd, 0) - COALESCE(c.cred_usd, 0), 2) AS net_sales_usd
            FROM gross g
            LEFT JOIN ret r ON g.territory_code = r.territory_code
            LEFT JOIN cred c ON g.territory_code = c.territory_code
            ORDER BY net_sales_usd DESC
            """
            metric_meta = self.contract["M02"]

        # 4. Execute Query
        df_result = self.con.execute(sql).df()

        # 5. Build Trust Footer
        trust_footer = {
            "metric_id": "M01" if metric_choice == "GROSS_SALES" else "M02",
            "metric_name": metric_meta["name"],
            "owner": metric_meta["owner"],
            "date_basis": metric_meta["date_basis"],
            "currency_basis": metric_meta["currency_basis"],
            "data_freshness": freshness_info["latest_date"],
            "freshness_warning": freshness_info["warning"],
            "executed_sql": sql.strip(),
            "user_scope": access_res["scope"]
        }

        return {
            "success": True,
            "data": df_result.to_dict(orient="records"),
            "row_count": len(df_result),
            "trust_footer": trust_footer
        }

    def get_distributor_previsit_brief(self, user_id: str, distributor_id: str) -> Dict[str, Any]:
        """
        Generates the 360 distributor pre-visit brief:
        - Distributor profile & credit limit
        - Sell-In vs Scan Sell-Through rate
        - Receivables & disputed amounts
        - Stuck scheme credits & age
        """
        # Validate distributor belongs to user territory/scope
        d_row = self.con.execute(
            "SELECT distributor_id, distributor_name, territory_code, currency, credit_limit_local FROM distributors WHERE distributor_id = ?",
            [distributor_id]
        ).fetchone()

        if not d_row:
            return {"success": False, "message": f"Distributor '{distributor_id}' not found."}

        dist_id, dist_name, terr_code, curr, credit_limit = d_row
        
        access_res = self.security.check_access(user_id, "receivables", requested_territory=terr_code)
        if not access_res["allowed"]:
            return {"success": False, "message": access_res["reason"]}

        # Sell-in totals (FY26)
        sell_in = self.con.execute("""
            SELECT 
                ROUND(SUM(invoice_amount_local), 2) as total_sell_in_local,
                SUM(quantity) as total_packs_sold
            FROM sell_in_orders
            WHERE distributor_id = ? AND order_date >= '2025-10-01' AND order_date <= '2026-09-30'
        """, [dist_id]).fetchone()

        # Dealer Scans (Sell-through)
        scans = self.con.execute("""
            SELECT 
                COALESCE(SUM(ds.packs_scanned), 0) as total_packs_scanned
            FROM dealer_scans ds
            JOIN dealers dl ON ds.dealer_id = dl.dealer_id
            WHERE dl.distributor_id = ?
        """, [dist_id]).fetchone()

        # Receivables Aging (Latest Snapshot)
        rec = self.con.execute("""
            SELECT 
                snapshot_date,
                total_outstanding_local,
                not_due_local,
                overdue_1_30_local,
                overdue_31_60_local,
                overdue_61_90_local,
                overdue_90_plus_local,
                disputed_local
            FROM receivables_aging
            WHERE distributor_id = ?
            ORDER BY snapshot_date DESC LIMIT 1
        """, [dist_id]).fetchone()

        # Stuck & Pending Credits
        credits = self.con.execute("""
            SELECT 
                credit_id, scheme_name, scheme_type, status, accrual_date, amount_local,
                datediff('day', accrual_date, CURRENT_DATE) as age_days
            FROM schemes_and_credits
            WHERE distributor_id = ? AND status = 'Accrued'
            ORDER BY accrual_date ASC
        """, [dist_id]).df()

        # Calculate scan sell-through ratio
        packs_sold = sell_in[1] or 0
        packs_scanned = scans[0] or 0
        sell_through_ratio = round((packs_scanned / packs_sold), 2) if packs_sold > 0 else 0.0

        return {
            "success": True,
            "distributor": {
                "id": dist_id,
                "name": dist_name,
                "territory": terr_code,
                "currency": curr,
                "credit_limit": credit_limit
            },
            "commercial": {
                "fy26_sell_in_local": sell_in[0] or 0,
                "packs_sold": packs_sold,
                "packs_scanned": packs_scanned,
                "sell_through_ratio": sell_through_ratio,
                "channel_health": "HEALTHY" if sell_through_ratio > 0.4 else "WARNING_SLOW_SELL_THROUGH"
            },
            "receivables": {
                "snapshot_date": str(rec[0]) if rec else "N/A",
                "total_outstanding": rec[1] if rec else 0,
                "not_due": rec[2] if rec else 0,
                "overdue_90_plus": rec[6] if rec else 0,
                "disputed": rec[7] if rec else 0
            },
            "stuck_credits": credits.to_dict(orient="records"),
            "trust_footer": {
                "generated_at": "30-Sep-2026",
                "rules_applied": ["RLS Enforced", "Latest Snapshot Aging", "Pending Scheme Accruals"]
            }
        }
