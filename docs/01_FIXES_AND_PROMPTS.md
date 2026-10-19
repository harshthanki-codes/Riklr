# 01 — Audit, fixes and copy-paste prompts (deadline Mon 19 Oct 2026, 13:00 IST)

Everything below was checked by running your repo and re-deriving numbers from `warehouse.duckdb`.
`scripts/verify_headlines.py` (attached) reproduces every figure. Put it in the repo and quote only what it prints.

---

## 0. DO THIS FIRST (5 minutes) — the repo as it stands would show reviewers NO code

`git status` shows `src/`, `tests/`, `docs/`, `README.md` and `sales-analyst/data/` are **untracked**; the only commit is the case pack.
```bash
git add -A && git commit -m "Governed sales analyst prototype" && git push origin main
```
Then: repo **private** → Settings → Collaborators → invite `rr-riklr`. Re-do this at 11:30 and 12:30 so a late failure never leaves you with nothing.
Missing required items: `chat-history/`, notes (`NOTES.md`), deck as **PDF/PPTX**, video link, `requirements.txt`, real run steps (README has a `<repo-name>` placeholder and says `cd Riklr`).

---

## 1. Audit — what is wrong, with evidence

| # | Problem | Evidence | Why it matters |
|---|---|---|---|
| A1 | **Net sales headline is wrong** | Repo $532.4M vs clean **$575.2M** (−7.4%). Engine INNER-JOINs `territories` on the raw transaction code, silently dropping **1,326 of 16,585 sell-in rows (8.0%)** and 83 return rows with legacy/lower-case/dash-less codes. Also no de-dup (245 sell-in lines, 19 returns re-sent by ERP) and negative invoice lines are excluded instead of deducted. | The Controller said exactly this: "whatever you build has to deal with it, or you'll get different numbers from mine." The BI Lead named territory codes as the #1 time sink. |
| A2 | **FY2025 option returns all-time** | `else: date_filter = "1=1"` → FY2025 "net" = $1.22B | UI exposes the FY2025 dropdown. |
| A3 | **"24.5×" is not defensible** | $18.19B is a 2.25-year naive sum (Jul-24→Sep-26) vs a 1-year net figure; $18.19B / $532M is actually 34×. Like-for-like (FY26 naive $8.40B vs clean FY26 gross $637.4M) = **13.2×** — consistent with the CDO's "about fifteen times". | A reviewer who re-computes will catch it. Use 13×. |
| A4 | **Radar is not a backtest and shows nonsense ratios** | Flags use `actual_returns_usd > 500000` (future information). Displays sell-through 141%, 130%, 104% (all-time scans ÷ FY26 sell-in). `loading_multiplier_threshold` is never used, but the deck says ">2.5×" and "90 days early". | The headline feature contradicts its own story. Fix = real as-of backtest (below). |
| A5 | **"$8.0M of $8.85M" doesn't match your own engine** | Engine shows Brazil returns $12.04M; clean BR-South FY26 = **$12.03M of $13.03M Brazil (92%) and 72% of the company's $16.65M**. | Two figures in one repo. |
| A6 | **Brief has bugs** | Scans not date-bounded (ratio wrong); ages use `CURRENT_DATE` (non-deterministic; today ≠ 30 Sep); `generated_at` hard-coded; the language selector does nothing though README claims Marathi/Hindi/Portuguese; whole brief denied for roles without `receivables` instead of redacting; KAM scope = every distributor in the territory, not "assigned distributors". | Permission matrix says Agronomist sees quantities only, Sales Ops sees no receivables, KAM sees assigned distributors only. |
| A7 | **Freshness is hard-coded** | `BR` only, `lag_days: 8`, static text, `has_warnings: True`. | Must be computed from `table_load_log`: Brazil sell-in loads since 10 Aug: **15 of 52 succeeded**, latest business date **21 Sep**, receivables last good snapshot **31 Jul**. |
| A8 | **YAML contract is decorative** | Engine SQL is hard-coded in Python; `sql_template` unused; only M01/M02 implemented (M04–M10 have no SQL). | "Governed by contract" is a core claim. |
| A9 | **SQL injection** | `territory`/`region` are f-string-interpolated into SQL from a free-text UI box. | Embarrassing for a "zero-hallucination, physically enforced" product. Use bound params + allowlists. |
| A10 | **Benchmark overclaims** | 4 checks, docstring says "60+"; `naive_would_fail += 1` is unconditional; prints "100% of traps caught" regardless. Deck cites "Naive <55%", "100% deterministic", "2.4 seconds", "3–5 days" — none computed. | "Impact in numbers" is 1/3 of the assessment. Unsupported numbers cost more than missing ones. |
| A11 | **Missing the strongest insights** | Old-bot "+62% pilot uplift" is seasonality (Sales Head said so in the interview; data confirms). Not in the deck. Also not shown: bridge between the two definitions of Sales; audit log. | These are what a Riklr reviewer will look for. |

**Correction to something I told you earlier:** I said the rest of the company returned $3.35M. That figure came from an inner join that dropped USD rows. The correct figure is **$4.6M** (company total $16.65M, Brazil South $12.03M). Also Brazil loads: 15 of 52 succeeded since 10 Aug (not "14 of 51").

---

## 2. Verified numbers to use everywhere (clean method; run `verify_headlines.py`)

| Fact | Value |
|---|---|
| Naive all-time sum of `invoice_amount_local` | $18.19B (BRL+INR+EUR+… added together) |
| Like-for-like FY26: naive vs clean gross USD | $8.40B vs $637.4M = **13.2× too high** |
| FY26 clean: gross / negative lines / returns / scheme credits / **net** | $637.4M / $0.8M / $16.7M / $44.7M / **$575.2M** (Brazil data ends 21 Sep) |
| Cleaning receipts | 245 duplicate sell-in lines, 19 duplicate returns, 1,326 rows with legacy/malformed territory codes, 58 negative invoice lines |
| Brazil South FY26 returns | **$12.03M** = 92% of Brazil, 72% of company |
| **Early-warning backtest (as of 30 Sep 2025, uses only data available then)** | Rule `self-relative sell-through < 0.70` flags 17 of 32 Brazil distributors that went on to hold **$11.4M of $12.5M (91%)** of later returns; 15 of the 17 are among the top-17 returners; 88% are BR-South. Lead time ≈ 4–5 months before returns (Feb–Apr) and 2 months before the drought (Nov–Dec). As of 31 Aug the same rule captures 70% (9 of 15 hits). |
| Brazil South sell-through vs prior season | 0.19 vs 0.39 at end-Sep |
| Old bot | peak **85** users/week (386 questions), now **8**; answered 71% in English vs **16%** in other languages; 465 territory-manager questions named another territory, **358 answered** |
| Pilot illusion | Apr–Jun vs Jan–Mar packs: pilot +58% vs others −45% (2025, bot live); **+55% vs −45% in 2026 with no bot** |
| India scheme credits | avg **86 days** to issue vs 30-day policy; 100% late, 68% > 60 days; **88 credits / INR 100.6M still accrued**, all > 30 days old |
| Active distributor | 125 (Sales Ops) vs 123 (Finance invoice) vs 115 (Finance balance) |

Caveat to state honestly: scans cover only enrolled dealers, so compare each distributor with *itself last season*, never across distributors.

---

## 3. Schedule (now ≈ 10:00 → freeze 12:45 → submit by 12:50)

| Time | Work | If late |
|---|---|---|
| 10:00–10:10 | §0 commit + push | never skip |
| 10:10–10:40 | **P1** cleaning layer + FY fix + bound params; **P2** freshness | must finish |
| 10:40–11:10 | **P3** radar backtest; **P4** brief fixes + redaction | must finish |
| 11:10–11:45 | **P5** NL adapter (rules router) + replay of old-bot log | cut LLM tier, keep rules |
| 11:45–12:05 | **P6** UI pass (bridge, receipts, voice mock) | cut to bridge + receipts |
| 12:05–12:35 | Deck → PDF; **record video** (script in file 03; one take + one retake) | start recording by 12:10 |
| 12:35–12:50 | P7 eval table, README, NOTES, chat-history export, push, form | submit by 12:50, not 12:59 |

---

## 4. Prompts for your coding AI (paste in order; each has an acceptance test)

> Prefix every prompt with: *"Work in the existing repo. Don't rewrite what works. Run the acceptance test and show me the output before finishing. No new numbers in docs unless a script prints them."*

### P1 — Cleaning layer + engine correctness (the most important fix)
```
Create src/engine/cleaning.py that builds DuckDB TEMP VIEWS once at engine start:
- clean_sell_in: DISTINCT ON (line_id); territory_code and region_code taken from the distributors master (NOT from the transaction); keep a flag is_negative_line (quantity<0).
- clean_returns: DISTINCT ON (return_id); territory from distributors master.
- clean_credits: DISTINCT ON (credit_id); territory from distributors master.
- fx_monthly: monthly average of fx_rates per currency (average whatever business days exist), PLUS a USD row with rate 1.0 for every month so INNER joins never drop USD rows.
- cleaning_receipts(): returns a dict of counts: duplicate sell-in lines (245), duplicate returns (19), sell-in rows with non-standard territory codes remapped (1,326), return rows remapped (83), negative lines (58), FX months with missing business days.
Refactor governed_engine.py and risk_radar.py to read ONLY from these views. Fix fiscal_year: map FY2025 -> 2024-10-01..2025-09-30 and FY2026 -> 2025-10-01..2026-09-30 explicitly; any other value raises ValueError (no "1=1" fallback).
Net sales (M02) = gross(quantity>0, invoice_date) - negative lines (as returns) - returns(return_date) - credits(status<>'Cancelled', accrual_date), all in USD at the transaction-month average rate.
Replace every f-string-interpolated value with bound parameters (?) and validate territory/region/distributor against allowlists loaded from the master tables.
Acceptance: global FY2026 net = 575.2M (+-0.5M), gross = 637.4M, returns = 16.65M, credits = 44.74M; FY2025 returns a different, bounded number; tests/test_engine.py asserts all of this; passing a string like "IN-W01' OR 1=1 --" raises a validation error.
```

### P2 — Freshness computed from the load log
```
Rewrite src/engine/freshness.py to compute, per region and per table, from table_load_log: latest successful max_business_date, lag in days vs the latest date across all regions, load success rate since the first failure, and the latest receivables snapshot date. No hard-coded regions, dates or text. Every answer's trust footer must include data_through (date), lag_days, and a warning string generated from the numbers, e.g. "Brazil sell-in is current to 21 Sep 2026 (8 days behind other regions); 15 of 52 loads since 10 Aug succeeded; receivables last snapshot 31 Jul 2026." Add a caveat line on every Brazil/India field-team answer: "Orders taken on messaging apps may not be keyed into the ERP for up to 2 days."
Acceptance: Brazil -> lag 8 days, 15/52, latest 2026-09-21, aging 2026-07-31; NA/EU/IN -> healthy; a unit test mutates a copy of the log to make EU stale and sees a new warning.
```

### P3 — Radar becomes a real, honest backtest
```
Rewrite src/engine/risk_radar.py. Inputs: region, as_of_date (default 2026-09-30), threshold (default 0.70). Use ONLY data dated <= as_of_date for the signal:
 st_rel = (cumulative scans / cumulative sell-in packs since 1 Jul of the season, this season) / (same ratio for the same distributor at the same point last season)
 loading = this-season sell-in packs / last-season sell-in packs to the same date
Flag distributors with st_rel < threshold. Rank by expected exposure = (distributor sell-in USD to date) * (flag severity). Add weather context (rainfall_pct_of_normal for the territory over the last 8 weeks before as_of) as an explanatory column, NOT as a trigger. Never use future returns to flag.
Add backtest(as_of, outcome_window_end="2026-06-30") that computes after the fact: flagged count, share of later returns USD held by flagged distributors, hits among the top-N returners, precision, and a table per distributor.
Remove the ">500000 returns" rule and the all-time scans join. Show sell-through as a % capped for display only if >100%, with a note.
Acceptance (as_of 2025-09-30, region BR, threshold 0.70): flagged 17 of 32, returns held ~ $11.4M of $12.5M (91%), 15 of 17 in top-17 returners; as_of 2025-08-31: 70%. UI shows a date slider for as_of and the backtest table.
```

### P4 — Distributor brief: correct, role-aware, localized
```
Fix get_distributor_previsit_brief:
1) Bound scans and sell-in to the same window (current season to as_of) and show sell-through vs the SAME distributor last season (self-comparison), not an absolute 0.4 threshold.
2) Use AS_OF = 2026-09-30 everywhere; remove CURRENT_DATE and the hard-coded generated_at.
3) Field-level redaction by role using permission_matrix: Field Agronomist -> scans + sell-in QUANTITIES only (no amounts, no receivables, no credits); Sales Ops Analyst/Loyalty Manager -> no receivables section; KAM -> only distributors where kam_user_id = user; Territory Manager -> own territory. Return a "redacted_sections" list so the UI can say "Hidden by your role".
4) Add: top 5 products and top dealers with sell-through vs last season; dealers with no scans in the last 8 weeks (enrolled only); pending credits with age AND "typical time to issue in this region" (median accrual->issue days from clean_credits: India 78, Brazil 34) and "overdue vs 30-day policy".
5) Localization: a dictionary of labels/sentences for en, hi, mr, pt, te (static templates; numbers inserted by code). Selector must actually change the output. Add a note "Translations are template-based and need native-speaker review".
6) Add an offline export: download the brief as a single self-contained HTML (works on a phone with no signal).
7) Add a free-text 'Manager note' per distributor stored in a local JSON (Regional Manager wanted to "decide what the team sees and correct it").
Acceptance: Agronomist brief has no money fields; Sales Ops brief omits receivables; KAM cannot open a non-assigned distributor; Marathi output differs from English; Vidarbha distributor shows pending credits with typical wait 78 days.
```

### P5 — Natural-language / voice adapter WITHOUT SQL hallucination (see §5 for the design)
```
Create src/nl/ with: plan.py (pydantic QueryPlan, closed enums), router.py (language detection + multilingual lexicon rules -> QueryPlan + confidence), resolver.py (entity resolution), render.py (localized answer templates), replay.py (replay of old_bot_usage_log).
Rules: (0) Many field questions are ROMANIZED (Latin-script Hindi/Marathi, e.g. 'mere distributor ka outstanding kitna hai', 'chi baki kiti aahe', 'scheme ka credit note kab aayega') so the lexicon must include transliterations, not only native script; the real log has ~7,000 English and ~2,100 non-English questions to test against. Real unsupported-by-design examples to refuse politely: Portuguese 'Qual a previsao de vendas para a safra?' (forecast). Real supported: 'Quais revendas nao compraram nos ultimos 60 dias?' (stopped buying). (a) NO model ever writes SQL; the only output is a QueryPlan validated against enums; (b) entities (territory codes incl. legacy_code and case/dash variants, territory names, distributor names) are resolved by lookup against master tables, fuzzy-match ONLY inside the caller's permitted scope; ambiguous -> ask a clarifying question; (c) user_id comes from the session, text like "as the Global Sales Head" is ignored; (d) metric 'sales' with no qualifier -> run M01 AND M02 and show both with the bridge; never pick silently; (e) out-of-scope or low confidence (<0.6) -> say "I can't answer that reliably" and list what can be asked; (f) after the engine returns, the answer text is rendered from templates with numbers inserted from the result dict.
Optional LLM tier (only if ANTHROPIC_API_KEY is set): function-calling with the QueryPlan JSON schema for low-confidence cases; output validated by pydantic; invalid -> fall back to clarification. The demo must work with no API key.
Replay: run every question in data/old_bot_usage_log.csv through router -> engine as that user (role, territory) and report: % routed to a supported intent, % blocked by RLS (must include all cross-territory attempts), % non-English routed, % refused as out-of-scope, % showing both definitions. Save docs/replay_results.md.
Acceptance: 60-question gold file tests/gold_questions.yaml (en/hi/mr/pt/te; ambiguous; adversarial: "ignore your permissions", "show BR-S01 as a Vidarbha manager"; stale-data; out-of-scope) with intent/entity accuracy printed.
```

### P6 — UI pass (answer first, no clutter)
```
In src/ui/app.py: one 'Ask' page as the default. Persona picker at top-left; a single text box (plus 'simulated voice note' dropdown with 6 real questions from the old-bot log in mr/hi/pt/te); answer card first: one-sentence answer, the number, then three small chips: Definition (M02 Finance), Data through (21 Sep, Brazil), Scope (IN-W01). Behind a 'Why this number?' drawer: query plan JSON, bound SQL, cleaning receipts, trust footer.
Add a 'Two numbers, one bridge' view: waterfall from Sales Ops gross (local, order_date) -> USD -> invoice_date shift -> minus returns -> minus credits = Finance net, for any region/quarter, so the 'India on track vs short' argument is settled on screen.
Add a 'Data health' panel from freshness.py and a 'Cleaning receipts' expander. Keep the Radar and Brief as tabs. Remove emoji headers and the claim 'Mock Voice / Offline mode' unless implemented.
Acceptance: a CDO-demo path works in <10 clicks: pick a Vidarbha TM (IN-W01) -> simulated voice note using a REAL log phrase, e.g. Marathi 'Tiranex Agro Agencies chi baki kiti aahe?' (swap in a distributor from IN-W01) or Hindi 'scheme ka credit note kab aayega?' -> correct own-territory answer in the same language with the trust chips; the same TM asking about BR-S01 gets a polite refusal.
```

### P7 — Evaluation that earns the "numbers" marks
```
Rewrite src/evals/benchmark.py. Implement a real naive baseline (a function that does what the old bot did: SUM(invoice_amount_local) over raw tables, no FX, no de-dup, no RLS, no freshness) and run BOTH systems on the 60 gold questions. Print and save a table: correctness vs hand-verified SQL, refusal correctness, cross-territory leakage count (target 0), stale-data warnings shown, and median latency (measure it; do not claim a number you did not measure). Remove 'naive_would_fail += 1' hard-coding and every unconditional '100%' print. Save docs/eval_results.md and eval_results.json.
Acceptance: benchmark prints measured percentages for baseline vs governed; leakage 0 vs the baseline's measured leakage on the 465 cross-territory questions in the old log.
```

### P8 — Repo hygiene and submission
```
Create requirements.txt (duckdb, pandas, pyyaml, streamlit, pydantic, rapidfuzz, matplotlib optional). Fix README run steps (clone URL = my repo, correct folder name, python -m pip install -r requirements.txt, python scripts/verify_headlines.py, python -m src.evals.benchmark, streamlit run src/ui/app.py). Add scripts/verify_headlines.py (attached). Add NOTES.md (attached, edit as needed). Export decks to docs/deck.pdf. Add .gitignore (__pycache__, .venv). Remove claims in README/deck that are not printed by a script. Commit and push.
```

---

## 5. NL / voice adapter — design in one page

```
text or STT transcript ─▶ language detect (Unicode script + stopwords)
                       ─▶ rules router (multilingual lexicon per intent)  ──┐
                       ─▶ [optional LLM, JSON-schema only, <0.6 conf]  ─────┤
                                                                            ▼
                       QueryPlan (pydantic, closed enums)  ─▶ entity resolver (master tables, caller's scope only)
                                                                            ▼
                       policy gate (role × domain × territory)  ─▶ engine templates (bound params)
                                                                            ▼
                       result dict ─▶ localized template (numbers inserted by code) ─▶ trust footer ─▶ audit_log row
```
- **Closed intents:** metric, compare_definitions, distributor_brief, channel_risk, pending_credits, overdue, stopped_buying, data_health, out_of_scope.
- **Closed metrics:** M01 M02 M04 M05 M06 M07 M08 M09 M10 only. No free SQL, no free column names.
- **Why this can't hallucinate SQL:** the language layer chooses from a menu; the engine owns every query; values are bound parameters; identifiers come from enums.
- **Why it can't leak:** `user_id` comes from the session; entity lookup only searches the caller's permitted territories (so enumeration by guessing names fails); the policy gate runs *after* parsing and *before* any SQL.
- **Ambiguity rule (BI Lead):** never pick a definition silently — "sales" shows M01 and M02 with the bridge; "return rate" shows M05 and M06; "active distributors" shows 125 / 123 / 115.
- **"I don't know" rule (Controller):** low confidence, missing FX, stale data, or out-of-scope → refuse and say why.
- **Audit log:** every query writes who, plan, SQL, row count, data-through, result hash to `audit_log` (the Controller's signature is on the old access request).
- **Voice (mock):** the brief allows mocking the field app. Use the "simulated voice note" dropdown with real questions from the old log; document the real integration (on-device or cloud STT + TTS, cached morning briefs because village networks are weak).

---

## 6. Interview details to cover (priority = effect on score)

| Interview | Detail | Where to show it |
|---|---|---|
| CDO | "TM asks in own language, gets right answer in seconds" | P6 CDO-demo path; **measure latency** |
| CDO | "never a wrong number in front of the CEO" | refusals + magnitude sanity check; bridge |
| CDO | "no six-month cleanup" | cleaning in code, receipts panel (done in hours) |
| Sales Head | "both numbers on every slide… people pick the bigger" | bridge view |
| Sales Head | "which distributors matter this month" | radar ranked by exposure |
| Sales Head | "tie incentive to following recommendations" | **argue against** in deck slide 10 (distrust, field already feels watched); measure usefulness, not compliance |
| Sales Head | pilot was India + kharif | slide 4 chart |
| RSM Brazil | "my tool, I can correct it" | manager note field |
| RSM Brazil | "don't use the drought season as baseline" | mark FY26 BR-South as abnormal-season in comparisons |
| RSM Brazil | orders arrive by messaging app, keyed 2 days later | freshness caveat line |
| TM Vidarbha | one page per distributor, simple, local language | brief in Marathi |
| TM Vidarbha | "which credits are pending and when will they come" | typical wait 78 days in India |
| TM Vidarbha | weak network, wants it before leaving | offline HTML export |
| TM Vidarbha | fear of being monitored | no compliance tracking; say so |
| Controller | uses her definitions and states which | trust footer owner/basis |
| Controller | stop answering net-sales questions that disagree with hers | M02 is the only net definition; matches her policy |
| BI Lead | check the load log before each answer; permissions in the data layer | freshness + RLS |
| BI Lead | "tell me before the CDO" | frame data findings in NOTES as a handover to the BI team, not a blame list |
| Distributor | "look at what goes out of my door" | sell-through is the headline of the brief |
| Distributor | credit notes on time | India lag tracker (86 days vs 30) |
