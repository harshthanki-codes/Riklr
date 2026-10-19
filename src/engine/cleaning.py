"""
DuckDB Data Cleaning & Master Key Reconciliation Layer
Builds TEMP VIEWS once at engine start:
- clean_sell_in: DISTINCT ON (order_id, line_id); territory and region mapped from distributors master; flag is_negative_line (quantity < 0)
- clean_returns: DISTINCT ON (return_id); territory from distributors master
- clean_credits: DISTINCT ON (credit_id); territory from distributors master
- fx_monthly: monthly average of fx_rates per currency with rate 1.0 for USD so INNER joins never drop USD rows
- cleaning_receipts(): audit counts of cleaned anomalies
"""
from typing import Dict, Any
import duckdb

def init_cleaning_layer(con: duckdb.DuckDBPyConnection):
    # 1. Monthly FX rates table with synthetic USD 1.0 rows
    con.execute("""
        CREATE OR REPLACE TEMP VIEW fx_monthly AS
        WITH rates_agg AS (
            SELECT 
                strftime(rate_date, '%Y-%m') as ym,
                currency,
                AVG(local_per_usd) as avg_rate
            FROM fx_rates
            GROUP BY 1, 2
        ),
        all_months AS (
            SELECT DISTINCT strftime(rate_date, '%Y-%m') as ym FROM fx_rates
        ),
        usd_rows AS (
            SELECT ym, 'USD' as currency, 1.0 as avg_rate FROM all_months
        )
        SELECT ym, currency, avg_rate FROM rates_agg
        UNION ALL
        SELECT ym, currency, avg_rate FROM usd_rows;
    """)

    # 2. Master territory reconciliation mapping
    # Maps raw territory codes (including lowercase, trailing spaces, and legacy pre-2023 CRM codes) to canonical territory_code
    con.execute("""
        CREATE OR REPLACE TEMP VIEW territory_master_map AS
        WITH canonical AS (
            SELECT 
                territory_code,
                legacy_code,
                region_code,
                sub_region,
                territory_name
            FROM territories
        )
        SELECT 
            t.territory_code AS raw_code,
            c.territory_code AS canonical_code,
            c.region_code,
            c.sub_region,
            c.territory_name
        FROM (SELECT DISTINCT territory_code FROM sell_in_orders UNION SELECT DISTINCT territory_code FROM returns) t
        LEFT JOIN canonical c 
          ON UPPER(TRIM(t.territory_code)) = c.territory_code
          OR UPPER(TRIM(t.territory_code)) = c.legacy_code;
    """)

    # 3. Clean sell-in orders
    # Deduplicates on (order_id, line_id) and attaches canonical territory & region from distributors master
    con.execute("""
        CREATE OR REPLACE TEMP VIEW clean_sell_in AS
        WITH deduped AS (
            SELECT 
                order_id,
                line_id,
                order_date,
                invoice_date,
                s.distributor_id,
                d.territory_code,
                d.region_code,
                s.product_id,
                s.doc_type,
                s.quantity,
                s.unit_price_local,
                s.discount_pct,
                s.invoice_amount_local,
                s.currency,
                CASE WHEN s.quantity < 0 THEN TRUE ELSE FALSE END AS is_negative_line,
                ROW_NUMBER() OVER (PARTITION BY order_id, line_id ORDER BY invoice_date DESC) as rn
            FROM sell_in_orders s
            LEFT JOIN distributors d ON s.distributor_id = d.distributor_id
        )
        SELECT * EXCLUDE (rn) FROM deduped WHERE rn = 1;
    """)

    # 4. Clean returns
    con.execute("""
        CREATE OR REPLACE TEMP VIEW clean_returns AS
        WITH deduped AS (
            SELECT 
                return_id,
                return_date,
                credit_note_date,
                r.distributor_id,
                d.territory_code,
                d.region_code,
                r.product_id,
                r.original_order_id,
                r.quantity,
                r.credit_amount_local,
                r.currency,
                r.reason,
                ROW_NUMBER() OVER (PARTITION BY return_id ORDER BY return_date DESC) as rn
            FROM returns r
            LEFT JOIN distributors d ON r.distributor_id = d.distributor_id
        )
        SELECT * EXCLUDE (rn) FROM deduped WHERE rn = 1;
    """)

    # 5. Clean schemes and credits
    con.execute("""
        CREATE OR REPLACE TEMP VIEW clean_credits AS
        WITH deduped AS (
            SELECT 
                credit_id,
                scheme_id,
                scheme_name,
                scheme_type,
                c.distributor_id,
                d.territory_code,
                d.region_code,
                c.currency,
                c.period_start,
                c.period_end,
                c.accrual_date,
                c.issue_date,
                c.status,
                c.amount_local,
                ROW_NUMBER() OVER (PARTITION BY credit_id ORDER BY accrual_date DESC) as rn
            FROM schemes_and_credits c
            LEFT JOIN distributors d ON c.distributor_id = d.distributor_id
        )
        SELECT * EXCLUDE (rn) FROM deduped WHERE rn = 1;
    """)

def get_cleaning_receipts(con: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
    dup_orders = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT order_id, line_id FROM sell_in_orders GROUP BY 1, 2 HAVING count(*) > 1
        )
    """).fetchone()[0]

    dup_returns = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT return_id FROM returns GROUP BY 1 HAVING count(*) > 1
        )
    """).fetchone()[0]

    unmapped_raw_sellin = con.execute("""
        SELECT COUNT(*) FROM sell_in_orders s
        LEFT JOIN territories t ON s.territory_code = t.territory_code
        WHERE t.territory_code IS NULL
    """).fetchone()[0]

    neg_lines = con.execute("SELECT COUNT(*) FROM sell_in_orders WHERE quantity < 0").fetchone()[0]

    return {
        "duplicate_sell_in_lines": dup_orders,  # 245
        "duplicate_returns": dup_returns,        # 19
        "remapped_territory_codes": unmapped_raw_sellin, # 1,326
        "negative_invoice_lines": neg_lines     # 58
    }
