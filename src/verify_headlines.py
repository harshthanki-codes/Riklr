"""
Reproducible headline numbers for the Riklr sales-analyst case.
Run from the repo root:  python scripts/verify_headlines.py
Every number quoted in the deck / video / README should print from here.
Cleaning rules (all documented in NOTES.md):
  * de-duplicate re-extracted rows (sell_in by line_id, returns by return_id, credits by credit_id)
  * territory = distributor master (fixes legacy / lower-case / dash-less codes on transactions)
  * FX = monthly average of the published daily rates for the transaction month (gaps just average what exists); USD rate = 1
  * negative invoice lines = returns (Finance policy), reported separately
"""
import sys, duckdb, pandas as pd
DB = sys.argv[1] if len(sys.argv) > 1 else "fde-case-study/sales-analyst/data/warehouse.duckdb"
con = duckdb.connect(DB, read_only=True)
FY26 = ("2025-10-01", "2026-09-30")
con.sql("""create or replace temp view fxm as
  select date_trunc('month',rate_date) m, currency c, avg(local_per_usd) r from fx_rates group by 1,2
  union all select m, 'USD', 1.0 from (select distinct date_trunc('month',rate_date) m from fx_rates)""")
con.sql("""create or replace temp view si as select distinct on (line_id) s.*, d.territory_code tc, d.region_code rg
  from sell_in_orders s join distributors d using(distributor_id) order by line_id""")
con.sql("""create or replace temp view rt as select distinct on (return_id) r.*, d.territory_code tc, d.region_code rg
  from returns r join distributors d using(distributor_id) order by return_id""")
con.sql("""create or replace temp view cr as select distinct on (credit_id) c.*, d.territory_code tc, d.region_code rg
  from schemes_and_credits c join distributors d using(distributor_id) order by credit_id""")
con.sql("create or replace temp view sc as select dl.distributor_id, week_start, packs_scanned from dealer_scans s join dealers dl using(dealer_id)")
one = lambda s: con.sql(s).fetchone()
out = {}

# 1. cleaning receipts
out["dup_sell_in_lines"] = one("select count(*)-count(distinct line_id) from sell_in_orders")[0]
out["dup_return_rows"] = one("select count(*)-count(distinct return_id) from returns")[0]
out["sell_in_rows_bad_territory_code"] = one("select count(*) from sell_in_orders where territory_code not in (select territory_code from territories)")[0]
out["sell_in_rows_total"] = one("select count(*) from sell_in_orders")[0]
out["negative_invoice_lines"] = one("select count(*) from sell_in_orders where quantity<0")[0]

# 2. naive vs governed (like for like)
naive_all = one("select sum(invoice_amount_local) from sell_in_orders")[0]
naive_fy26 = one(f"select sum(invoice_amount_local) from sell_in_orders where order_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
gross = one(f"select sum(invoice_amount_local/f.r) from si join fxm f on f.m=date_trunc('month',si.invoice_date) and f.c=si.currency where quantity>0 and invoice_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
neg = one(f"select sum(-invoice_amount_local/f.r) from si join fxm f on f.m=date_trunc('month',si.invoice_date) and f.c=si.currency where quantity<0 and invoice_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
ret = one(f"select sum(credit_amount_local/f.r) from rt join fxm f on f.m=date_trunc('month',rt.return_date) and f.c=rt.currency where return_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
cred = one(f"select sum(amount_local/f.r) from cr join fxm f on f.m=date_trunc('month',cr.accrual_date) and f.c=cr.currency where status<>'Cancelled' and accrual_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
out.update(naive_alltime_bn=naive_all/1e9, naive_fy26_bn=naive_fy26/1e9, gross_usd_m=gross/1e6, neg_lines_usd_m=neg/1e6,
           returns_usd_m=ret/1e6, scheme_credits_usd_m=cred/1e6, net_sales_usd_m=(gross-neg-ret-cred)/1e6,
           like_for_like_overstatement_x=naive_fy26/gross)

# 3. Brazil South returns
brs = one(f"select sum(credit_amount_local/f.r) from rt join fxm f on f.m=date_trunc('month',rt.return_date) and f.c=rt.currency where tc like 'BR-S%' and return_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
brt = one(f"select sum(credit_amount_local/f.r) from rt join fxm f on f.m=date_trunc('month',rt.return_date) and f.c=rt.currency where rg='BR' and return_date between date '{FY26[0]}' and date '{FY26[1]}'")[0]
out.update(br_south_returns_usd_m=brs/1e6, brazil_returns_usd_m=brt/1e6, br_south_share_of_brazil=brs/brt, br_south_share_of_company=brs/ret)

# 4. Honest early-warning backtest (only data available at the as-of date is used for the signal)
def backtest(asof="2025-09-30", thr=0.70):
    py = (pd.Timestamp(asof) - pd.DateOffset(years=1)).date()
    s = con.execute(f"""
    with cur as (select distributor_id, sum(quantity) si_c from si where rg='BR' and quantity>0 and order_date between date '2025-07-01' and date '{asof}' group by 1),
    prv as (select distributor_id, sum(quantity) si_p from si where rg='BR' and quantity>0 and order_date between date '2024-07-01' and date '{py}' group by 1),
    sc_c as (select distributor_id, sum(packs_scanned) x from sc where week_start between date '2025-07-01' and date '{asof}' group by 1),
    sc_p as (select distributor_id, sum(packs_scanned) x from sc where week_start between date '2024-07-01' and date '{py}' group by 1),
    ret as (select distributor_id, sum(credit_amount_local/f.r) u from rt join fxm f on f.m=date_trunc('month',rt.return_date) and f.c=rt.currency where return_date>date '{asof}' and return_date<=date '2026-06-30' group by 1)
    select d.distributor_id, d.territory_code tc, cur.si_c, prv.si_p, sc_c.x scc, sc_p.x scp, coalesce(ret.u,0) ret_usd
    from distributors d join cur using(distributor_id) join prv using(distributor_id) left join sc_c using(distributor_id) left join sc_p using(distributor_id) left join ret using(distributor_id)
    where d.region_code='BR'""").df()
    s["st_rel"] = (s.scc / s.si_c) / (s.scp / s.si_p)
    f = s[s.st_rel < thr]; top = s.nlargest(len(f), "ret_usd")
    return dict(asof=asof, flagged=len(f), distributors=len(s), later_returns_usd_m=s.ret_usd.sum()/1e6,
                flagged_returns_usd_m=f.ret_usd.sum()/1e6, share_of_returns=f.ret_usd.sum()/s.ret_usd.sum(),
                hit_top_returners=len(set(f.distributor_id) & set(top.distributor_id)), brs_share_of_flagged=f.tc.str.startswith("BR-S").mean())
out["backtest_2025-09-30"] = backtest("2025-09-30")
out["backtest_2025-08-31"] = backtest("2025-08-31")

# 5. Freshness (computed, not hard-coded)
fr = con.sql("""select count(*) n, sum((status='Success')::int) ok, max(max_business_date) mx from table_load_log
  where table_name='sell_in_orders' and region='BR' and load_started_at>=timestamp '2026-08-10'""").fetchone()
out["brazil_loads_since_aug10"] = dict(total=fr[0], success=fr[1], latest_business_date=str(fr[2]))
out["brazil_aging_last_success"] = str(one("select max(max_business_date) from table_load_log where table_name='receivables_aging' and region='BR' and status='Success'")[0])

# 6. India scheme credits
c = con.sql("""select count(*) n, avg(date_diff('day',accrual_date,issue_date)) avg_lag, avg((date_diff('day',accrual_date,issue_date)>30)::int) p30, avg((date_diff('day',accrual_date,issue_date)>60)::int) p60
  from cr where status='Issued' and rg='IN'""").fetchone()
p = con.sql("select count(*), sum(amount_local) from cr where status='Accrued' and rg='IN'").fetchone()
out["india_credits"] = dict(issued=c[0], avg_days_to_issue=c[1], pct_over_30d=c[2], pct_over_60d=c[3], pending_n=p[0], pending_inr_m=p[1]/1e6)

# 7. Old bot
b = con.sql("""with w as (select date_trunc('week',asked_at::timestamp) wk, count(distinct user_id) u from old_bot_usage_log group by 1)
  select max(u), (select u from w order by wk desc limit 1) from w""").fetchone()
out["bot_peak_weekly_users"], out["bot_latest_weekly_users"] = b
lang = con.sql("""select avg((status='Answered')::int) filter (where language_detected='en'), avg((status='Answered')::int) filter (where language_detected<>'en') from old_bot_usage_log""").fetchone()
out["bot_answered_pct_en"], out["bot_answered_pct_non_en"] = lang
def packs(a, b2, grp):
    return one(f"""select sum(quantity) from si where quantity>0 and order_date between date '{a}' and date '{b2}' and {grp}""")[0]
pil = "(rg='IN' or tc='EU-UK1')"; oth = "not (rg='IN' or tc='EU-UK1')"
for yr in (2025, 2026):
    q1, q2 = (f"{yr}-01-01", f"{yr}-03-31"), (f"{yr}-04-01", f"{yr}-06-30")
    out[f"pilot_vs_other_packs_{yr}"] = dict(pilot_pct=packs(*q2, pil)/packs(*q1, pil)-1, other_pct=packs(*q2, oth)/packs(*q1, oth)-1)

pd.set_option("display.width", 200)
for k, v in out.items(): print(f"{k:38s} {v}")

# guard rails: fail loudly if the story drifts
assert abs(out["net_sales_usd_m"] - 575.2) < 1.0, out["net_sales_usd_m"]
assert 13.0 < out["like_for_like_overstatement_x"] < 13.5
assert abs(out["br_south_returns_usd_m"] - 12.03) < 0.1
assert out["backtest_2025-09-30"]["share_of_returns"] > 0.85
print("\nALL HEADLINE ASSERTIONS PASSED")
