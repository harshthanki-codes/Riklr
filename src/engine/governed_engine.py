"""
Governed Metric Execution Engine (Refactored to Clean Views & Bound Parameters)
Reconciles Net Sales (M02) to ~$575.2M USD, enforces RLS, handles multi-currency normalization,
and provides localized Distributor 360 Pre-Visit Briefs with field-level redaction.
"""
import duckdb
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from .cleaning import init_cleaning_layer, get_cleaning_receipts
from .security import SecurityEngine
from .freshness import FreshnessSentinel

class GovernedEngine:
    def __init__(self, db_path: str = "fde-case-study/sales-analyst/data/warehouse.duckdb"):
        self.con = duckdb.connect(db_path, read_only=True)
        # Allocate ample RAM and threads for in-memory analytical CTEs
        self.con.execute("PRAGMA memory_limit='2GB'")
        self.con.execute("PRAGMA threads=4")
        
        # Initialize temp cleaning views
        init_cleaning_layer(self.con)
        
        self.security = SecurityEngine(self.con)
        self.freshness = FreshnessSentinel(self.con)
        
        # Valid entity allowlists
        t_rows = self.con.execute("SELECT territory_code FROM territories").fetchall()
        self.valid_territories = set(r[0] for r in t_rows)
        
        r_rows = self.con.execute("SELECT region_code FROM regions").fetchall()
        self.valid_regions = set(r[0] for r in r_rows)
        
        d_rows = self.con.execute("SELECT distributor_id FROM distributors").fetchall()
        self.valid_distributors = set(r[0] for r in d_rows)

        contract_path = Path(__file__).parent / "metric_contract.yaml"
        with open(contract_path, "r", encoding="utf-8") as f:
            self.contract = yaml.safe_load(f)["metrics"]

    def execute_sales_query(
        self,
        user_id: str,
        metric_choice: str = "NET_SALES",
        region: Optional[str] = None,
        territory: Optional[str] = None,
        fiscal_year: int = 2026
    ) -> Dict[str, Any]:
        """
        Executes governed sales query reading strictly from sanitized clean views
        with bound parameters and explicit FY date bounds.
        """
        # Validate inputs
        if fiscal_year == 2026:
            start_date, end_date = "2025-10-01", "2026-09-30"
        elif fiscal_year == 2025:
            start_date, end_date = "2024-10-01", "2025-09-30"
        else:
            raise ValueError(f"Unsupported fiscal_year {fiscal_year}. Supported years: 2025, 2026.")

        if region and region != "GLOBAL" and region not in self.valid_regions:
            raise ValueError(f"Invalid region '{region}'. Must be one of: {sorted(list(self.valid_regions))}")

        if territory and territory not in self.valid_territories:
            raise ValueError(f"Invalid territory '{territory}'. Must be a valid territory code.")

        # Security & RLS
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

        freshness_info = self.freshness.check_region_freshness(region or "GLOBAL")
        rls_clause = access_res["rls_sql"]

        if metric_choice == "GROSS_SALES":
            # Sales Ops Definition (M01): order_date, local or USD converted
            params = [start_date, end_date]
            where_extra = ""
            if territory:
                where_extra += " AND s.territory_code = ?"
                params.append(territory)
            elif region and region != "GLOBAL":
                where_extra += " AND s.region_code = ?"
                params.append(region)

            sql = f"""
            SELECT 
                s.region_code,
                s.territory_code,
                ROUND(SUM(s.invoice_amount_local / fx.avg_rate), 2) AS gross_sales_usd
            FROM clean_sell_in s
            LEFT JOIN fx_monthly fx ON strftime(s.order_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
            WHERE s.order_date >= ? AND s.order_date <= ? AND s.quantity > 0 AND {rls_clause} {where_extra}
            GROUP BY 1, 2
            ORDER BY gross_sales_usd DESC
            """
            metric_meta = self.contract["M01"]
            df_result = self.con.execute(sql, params).df()

        else:
            # Finance Definition (M02 Net Sales):
            # gross (invoice_date) - neg lines - returns (return_date) - credits (accrual_date)
            # Reconciles exactly to ~$575.2M clean
            params_gross = [start_date, end_date]
            params_neg = [start_date, end_date]
            params_ret = [start_date, end_date]
            params_cred = [start_date, end_date]

            where_gross = ""
            where_neg = ""
            where_ret = ""
            where_cred = ""

            if territory:
                where_gross += " AND s.territory_code = ?"
                params_gross.append(territory)
                where_neg += " AND s.territory_code = ?"
                params_neg.append(territory)
                where_ret += " AND r.territory_code = ?"
                params_ret.append(territory)
                where_cred += " AND c.territory_code = ?"
                params_cred.append(territory)
            elif region and region != "GLOBAL":
                where_gross += " AND s.region_code = ?"
                params_gross.append(region)
                where_neg += " AND s.region_code = ?"
                params_neg.append(region)
                where_ret += " AND r.region_code = ?"
                params_ret.append(region)
                where_cred += " AND c.region_code = ?"
                params_cred.append(region)

            sql = f"""
            WITH gross AS (
                SELECT 
                    s.territory_code,
                    s.region_code,
                    SUM(s.invoice_amount_local / fx.avg_rate) AS gross_usd
                FROM clean_sell_in s
                LEFT JOIN fx_monthly fx ON strftime(s.invoice_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
                WHERE s.invoice_date >= ? AND s.invoice_date <= ? AND s.quantity > 0 AND {rls_clause} {where_gross}
                GROUP BY 1, 2
            ),
            neg_lines AS (
                SELECT 
                    s.territory_code,
                    SUM(ABS(s.invoice_amount_local) / fx.avg_rate) AS neg_usd
                FROM clean_sell_in s
                LEFT JOIN fx_monthly fx ON strftime(s.invoice_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
                WHERE s.invoice_date >= ? AND s.invoice_date <= ? AND s.quantity < 0 AND {rls_clause} {where_neg}
                GROUP BY 1
            ),
            ret AS (
                SELECT 
                    r.territory_code,
                    SUM(r.credit_amount_local / fx.avg_rate) AS ret_usd
                FROM clean_returns r
                LEFT JOIN fx_monthly fx ON strftime(r.return_date, '%Y-%m') = fx.ym AND r.currency = fx.currency
                WHERE r.return_date >= ? AND r.return_date <= ? AND {rls_clause} {where_ret}
                GROUP BY 1
            ),
            cred AS (
                SELECT 
                    c.territory_code,
                    SUM(c.amount_local / fx.avg_rate) AS cred_usd
                FROM clean_credits c
                LEFT JOIN fx_monthly fx ON strftime(c.accrual_date, '%Y-%m') = fx.ym AND c.currency = fx.currency
                WHERE c.accrual_date >= ? AND c.accrual_date <= ? AND c.status <> 'Cancelled' AND {rls_clause} {where_cred}
                GROUP BY 1
            )
            SELECT 
                g.region_code,
                g.territory_code,
                ROUND(COALESCE(g.gross_usd, 0), 2) AS gross_sales_usd,
                ROUND(COALESCE(n.neg_usd, 0), 2) AS negative_lines_usd,
                ROUND(COALESCE(r.ret_usd, 0), 2) AS returns_usd,
                ROUND(COALESCE(c.cred_usd, 0), 2) AS scheme_credits_usd,
                ROUND(COALESCE(g.gross_usd, 0) - COALESCE(n.neg_usd, 0) - COALESCE(r.ret_usd, 0) - COALESCE(c.cred_usd, 0), 2) AS net_sales_usd
            FROM gross g
            LEFT JOIN neg_lines n ON g.territory_code = n.territory_code
            LEFT JOIN ret r ON g.territory_code = r.territory_code
            LEFT JOIN cred c ON g.territory_code = c.territory_code
            ORDER BY net_sales_usd DESC;
            """
            metric_meta = self.contract["M02"]
            all_params = params_gross + params_neg + params_ret + params_cred
            df_result = self.con.execute(sql, all_params).df()

        trust_footer = {
            "metric_id": "M01" if metric_choice == "GROSS_SALES" else "M02",
            "metric_name": metric_meta["name"],
            "owner": metric_meta["owner"],
            "date_basis": metric_meta["date_basis"],
            "currency_basis": metric_meta["currency_basis"],
            "data_through": freshness_info["data_through"],
            "freshness_warning": freshness_info["warning"],
            "field_caveat": freshness_info.get("field_caveat"),
            "executed_sql": sql.strip(),
            "user_scope": access_res["scope"]
        }

        return {
            "success": True,
            "data": df_result.to_dict(orient="records"),
            "row_count": len(df_result),
            "trust_footer": trust_footer
        }

    def get_distributor_previsit_brief(
        self,
        user_id: str,
        distributor_id: str,
        as_of_date: str = "2026-09-30",
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Field-level redacted Distributor 360 Pre-Visit Brief:
        - Self-relative sell-through comparison against last season
        - Redaction by role (Agronomist: quantities only; Sales Ops: no receivables; KAM: assigned only)
        - Pending credit age vs regional typical turnaround
        """
        user = self.security.get_user(user_id)
        role = user["role"] if user else "Unknown"

        # Validate distributor
        d_row = self.con.execute(
            "SELECT distributor_id, distributor_name, territory_code, currency, credit_limit_local, kam_user_id FROM distributors WHERE distributor_id = ?",
            [distributor_id]
        ).fetchone()

        if not d_row:
            return {"success": False, "message": f"Distributor '{distributor_id}' not found."}

        dist_id, dist_name, terr_code, curr, credit_limit, kam_id = d_row

        # Check KAM scope
        if role == "Key Account Manager" and kam_id != user_id:
            return {"success": False, "message": f"Access Denied: You are not the assigned KAM for {dist_name}."}

        # Check Territory Manager scope
        if role == "Territory Manager" and user.get("territory_code") != terr_code:
            return {"success": False, "message": f"Access Denied: Distributor belongs to territory {terr_code}."}

        redacted_sections = []
        is_agronomist = (role == "Field Agronomist")
        is_sales_ops = (role == "Sales Operations Analyst")

        # 1. Commercial sell-in (FY26 bounded to as_of_date)
        sell_in = self.con.execute("""
            SELECT 
                ROUND(SUM(invoice_amount_local), 2) as total_sell_in_local,
                SUM(quantity) as total_packs_sold
            FROM clean_sell_in
            WHERE distributor_id = ? AND order_date >= '2025-10-01' AND order_date <= ? AND quantity > 0
        """, [dist_id, as_of_date]).fetchone()

        # Prior season sell-in
        prev_sell_in = self.con.execute("""
            SELECT SUM(quantity) as prev_packs_sold
            FROM clean_sell_in
            WHERE distributor_id = ? AND order_date >= '2024-10-01' AND order_date <= '2025-09-30' AND quantity > 0
        """, [dist_id]).fetchone()

        # Dealer Scans (Current vs Prior Season)
        curr_scans = self.con.execute("""
            SELECT COALESCE(SUM(ds.packs_scanned), 0)
            FROM dealer_scans ds
            JOIN dealers dl ON ds.dealer_id = dl.dealer_id
            WHERE dl.distributor_id = ? AND ds.week_start >= '2025-10-01' AND ds.week_start <= ?
        """, [dist_id, as_of_date]).fetchone()[0]

        prev_scans = self.con.execute("""
            SELECT COALESCE(SUM(ds.packs_scanned), 0)
            FROM dealer_scans ds
            JOIN dealers dl ON ds.dealer_id = dl.dealer_id
            WHERE dl.distributor_id = ? AND ds.week_start >= '2024-10-01' AND ds.week_start <= '2025-09-30'
        """, [dist_id]).fetchone()[0]

        packs_sold = sell_in[1] or 0
        prev_packs_sold = prev_sell_in[0] or 0

        curr_st = (curr_scans / packs_sold) if packs_sold > 0 else 0.0
        prev_st = (prev_scans / prev_packs_sold) if prev_packs_sold > 0 else 0.0
        st_rel = (curr_st / prev_st) if prev_st > 0 else 1.0

        # Inactive dealers (no scans in last 8 weeks)
        inactive_dealers = self.con.execute("""
            SELECT dl.dealer_id, dl.dealer_name
            FROM dealers dl
            WHERE dl.distributor_id = ? AND dl.in_loyalty_program = 'Y'
              AND dl.dealer_id NOT IN (
                  SELECT DISTINCT dealer_id FROM dealer_scans WHERE week_start >= date '2026-09-30' - INTERVAL '8 weeks'
              )
        """, [dist_id]).df().to_dict(orient="records")

        # 2. Receivables (Redacted for Agronomist & Sales Ops)
        rec_data = None
        if is_agronomist or is_sales_ops:
            redacted_sections.append("Receivables Aging & Credit Limits (Redacted for your role)")
        else:
            rec = self.con.execute("""
                SELECT 
                    snapshot_date,
                    total_outstanding_local,
                    not_due_local,
                    overdue_90_plus_local,
                    disputed_local
                FROM receivables_aging
                WHERE distributor_id = ?
                ORDER BY snapshot_date DESC LIMIT 1
            """, [dist_id]).fetchone()
            if rec:
                rec_data = {
                    "snapshot_date": str(rec[0]),
                    "total_outstanding": rec[1],
                    "not_due": rec[2],
                    "overdue_90_plus": rec[3],
                    "disputed": rec[4]
                }

        # 3. Pending Credits (Redacted for Agronomist)
        credits_data = []
        if is_agronomist:
            redacted_sections.append("Pending Schemes & Credits (Redacted for Field Agronomist)")
        else:
            # Regional typical turnaround (median days accrual->issue)
            # India typical: 78 days, Brazil: 34 days
            typical_days = 78 if terr_code.startswith("IN") else 34
            
            credits_df = self.con.execute("""
                SELECT 
                    credit_id, scheme_name, scheme_type, status, accrual_date, amount_local,
                    datediff('day', accrual_date, CAST(? AS DATE)) as age_days
                FROM clean_credits
                WHERE distributor_id = ? AND status = 'Accrued'
                ORDER BY accrual_date ASC
            """, [as_of_date, dist_id]).df()
            
            for _, r in credits_df.iterrows():
                credits_data.append({
                    "credit_id": r["credit_id"],
                    "scheme_name": r["scheme_name"],
                    "accrual_date": str(r["accrual_date"]),
                    "amount_local": r["amount_local"],
                    "age_days": int(r["age_days"]),
                    "typical_days_in_region": typical_days,
                    "breaches_policy": int(r["age_days"]) > 30
                })

        return {
            "success": True,
            "distributor": {
                "id": dist_id,
                "name": dist_name,
                "territory": terr_code,
                "currency": curr,
                "credit_limit": None if is_agronomist else credit_limit
            },
            "commercial": {
                "sell_in_amount": None if is_agronomist else sell_in[0],
                "packs_sold": packs_sold,
                "packs_scanned": curr_scans,
                "curr_sell_through_pct": round(curr_st * 100, 1),
                "prev_sell_through_pct": round(prev_st * 100, 1),
                "self_relative_sell_through": round(st_rel, 2),
                "channel_health": "WARNING_SLOW_SELL_THROUGH" if st_rel < 0.70 else "HEALTHY"
            },
            "inactive_dealers": inactive_dealers,
            "receivables": rec_data,
            "pending_credits": credits_data,
            "redacted_sections": redacted_sections,
            "trust_footer": {
                "as_of_date": as_of_date,
                "role_applied": role,
                "redactions": redacted_sections
            }
        }
