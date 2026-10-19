"""
Channel-Risk Radar Sentinel
Evaluates relative sell-through (st_rel) as of a specific date using strictly historical data.
st_rel = (scans_this_season / sellin_this_season) / (scans_last_season / sellin_last_season)
Flags distributors with st_rel < threshold.
Provides true backtest against later return realizations without data leakage.
"""
from typing import Dict, Any, List, Optional
import duckdb

class ChannelRiskRadar:
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def scan_channel_risks(
        self,
        region_code: str = "BR",
        as_of_date: str = "2025-09-30",
        threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """
        Calculates relative scan sell-through strictly as of as_of_date.
        """
        # Determine season start based on hemisphere/region (for Brazil, July 1)
        # Season 2025/26: 2025-07-01 to as_of_date
        # Season 2024/25: 2024-07-01 to same day-month last year
        query = f"""
        WITH curr_sell_in AS (
            SELECT 
                d.distributor_id,
                d.distributor_name,
                d.territory_code,
                t.territory_name,
                SUM(s.quantity) as curr_sellin_packs,
                SUM(s.invoice_amount_local / fx.avg_rate) as curr_sellin_usd
            FROM clean_sell_in s
            JOIN distributors d ON s.distributor_id = d.distributor_id
            JOIN territories t ON d.territory_code = t.territory_code
            LEFT JOIN fx_monthly fx ON strftime(s.invoice_date, '%Y-%m') = fx.ym AND s.currency = fx.currency
            WHERE t.region_code = '{region_code}'
              AND s.order_date >= CAST('2025-07-01' AS DATE) 
              AND s.order_date <= CAST('{as_of_date}' AS DATE)
              AND s.quantity > 0
            GROUP BY 1, 2, 3, 4
        ),
        prev_sell_in AS (
            SELECT 
                s.distributor_id,
                SUM(s.quantity) as prev_sellin_packs
            FROM clean_sell_in s
            JOIN distributors d ON s.distributor_id = d.distributor_id
            JOIN territories t ON d.territory_code = t.territory_code
            WHERE t.region_code = '{region_code}'
              AND s.order_date >= CAST('2024-07-01' AS DATE) 
              AND s.order_date <= (CAST('{as_of_date}' AS DATE) - INTERVAL '1 year')
              AND s.quantity > 0
            GROUP BY 1
        ),
        curr_scans AS (
            SELECT 
                dl.distributor_id,
                SUM(ds.packs_scanned) as curr_scans
            FROM dealer_scans ds
            JOIN dealers dl ON ds.dealer_id = dl.dealer_id
            WHERE ds.week_start >= CAST('2025-07-01' AS DATE) 
              AND ds.week_start <= CAST('{as_of_date}' AS DATE)
            GROUP BY 1
        ),
        prev_scans AS (
            SELECT 
                dl.distributor_id,
                SUM(ds.packs_scanned) as prev_scans
            FROM dealer_scans ds
            JOIN dealers dl ON ds.dealer_id = dl.dealer_id
            WHERE ds.week_start >= CAST('2024-07-01' AS DATE) 
              AND ds.week_start <= (CAST('{as_of_date}' AS DATE) - INTERVAL '1 year')
            GROUP BY 1
        ),
        weather AS (
            SELECT 
                territory_code,
                AVG(rainfall_pct_of_normal) as recent_rainfall_pct
            FROM weather_weekly
            WHERE week_start >= (CAST('{as_of_date}' AS DATE) - INTERVAL '8 weeks')
              AND week_start <= CAST('{as_of_date}' AS DATE)
            GROUP BY 1
        )
        SELECT 
            c.distributor_id,
            c.distributor_name,
            c.territory_code,
            c.territory_name,
            c.curr_sellin_packs,
            COALESCE(cs.curr_scans, 0) as curr_scans,
            COALESCE(p.prev_sellin_packs, 0) as prev_sellin_packs,
            COALESCE(ps.prev_scans, 0) as prev_scans,
            c.curr_sellin_usd,
            COALESCE(w.recent_rainfall_pct, 100.0) as recent_rainfall_pct
        FROM curr_sell_in c
        LEFT JOIN prev_sell_in p ON c.distributor_id = p.distributor_id
        LEFT JOIN curr_scans cs ON c.distributor_id = cs.distributor_id
        LEFT JOIN prev_scans ps ON c.distributor_id = ps.distributor_id
        LEFT JOIN weather w ON c.territory_code = w.territory_code
        ORDER BY c.curr_sellin_usd DESC;
        """
        df = self.con.execute(query).df()
        
        flagged = []
        for _, r in df.iterrows():
            c_sell = r['curr_sellin_packs'] or 0
            c_scan = r['curr_scans'] or 0
            p_sell = r['prev_sellin_packs'] or 0
            p_scan = r['prev_scans'] or 0

            curr_ratio = (c_scan / c_sell) if c_sell > 0 else 0.0
            prev_ratio = (p_scan / p_sell) if p_sell > 0 else 0.0
            
            st_rel = (curr_ratio / prev_ratio) if prev_ratio > 0 else (0.5 if curr_ratio < 0.2 else 1.0)
            
            if st_rel < threshold:
                flagged.append({
                    "distributor_id": r["distributor_id"],
                    "distributor_name": r["distributor_name"],
                    "territory": f"{r['territory_code']} ({r['territory_name']})",
                    "territory_code": r["territory_code"],
                    "curr_sellin_usd": float(r["curr_sellin_usd"]),
                    "curr_sell_through": curr_ratio,
                    "prev_sell_through": prev_ratio,
                    "st_rel": round(st_rel, 2),
                    "rainfall_pct_8w": round(float(r["recent_rainfall_pct"]), 1),
                    "risk_severity": "CRITICAL" if st_rel < 0.4 else "HIGH"
                })

        return flagged

    def run_backtest(self, as_of_date: str = "2025-09-30", threshold: float = 0.70) -> Dict[str, Any]:
        """
        Executes backtest comparing flagged distributors as of as_of_date against
        subsequent return volume up to end of FY2026.
        """
        flagged = self.scan_channel_risks(region_code="BR", as_of_date=as_of_date, threshold=threshold)
        flagged_ids = [f["distributor_id"] for f in flagged]

        # Returns realized strictly after as_of_date
        returns_summary = self.con.execute(f"""
            SELECT 
                r.distributor_id,
                SUM(r.credit_amount_local / fx.avg_rate) as later_returns_usd
            FROM clean_returns r
            LEFT JOIN fx_monthly fx ON strftime(r.return_date, '%Y-%m') = fx.ym AND r.currency = fx.currency
            WHERE r.return_date > '{as_of_date}' AND r.return_date <= '2026-09-30'
            GROUP BY 1
        """).df()

        later_returns_map = dict(zip(returns_summary['distributor_id'], returns_summary['later_returns_usd']))
        total_later_returns = sum(later_returns_map.values())
        
        flagged_returns = sum(later_returns_map.get(d_id, 0.0) for d_id in flagged_ids)
        share = (flagged_returns / total_later_returns) if total_later_returns > 0 else 0.0

        # Hits among top returners
        top_returners = sorted(later_returns_map.items(), key=lambda x: x[1], reverse=True)[:len(flagged)]
        top_ids = set([x[0] for x in top_returners])
        hits = len(set(flagged_ids).intersection(top_ids))

        br_south_count = sum(1 for f in flagged if f["territory_code"].startswith("BR-S"))

        return {
            "as_of_date": as_of_date,
            "flagged_count": len(flagged),
            "total_later_returns_usd": total_later_returns,
            "flagged_later_returns_usd": flagged_returns,
            "share_of_returns": round(share, 3),
            "hits_in_top_returners": hits,
            "br_south_share": round(br_south_count / len(flagged), 2) if flagged else 0.0,
            "flagged_distributors": flagged
        }
