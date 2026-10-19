# NOTES — research, method and assumptions
Candidate: iitmcs_24091540 · Case: sales-analyst · Data: warehouse extract as of 30 Sep 2026

## 1. What I did
Read the brief, 8 context documents, and 7 interviews (CDO, Global Sales Head, RSM Brazil South, TM Vidarbha, Global Finance Controller, Data & BI Lead, Distributor owner). Then tested what people said against the warehouse (the brief warns interviews "may not match the data"). Every figure in the deck prints from `scripts/verify_headlines.py`.

## 2. Where the interviews and the data disagree
| Said | Data |
|---|---|
| "Hundreds of users a week" (CDO) | Peak 85, now 8 (`old_bot_usage_log`) |
| "Pilot territories grew 62%" (launch note) | India kharif + UK; same jump in 2026 with no bot (+55% vs −45%) |
| "Brazil is basically caught up" (BI lead) | 15 of 52 loads since 10 Aug succeeded; data ends 21 Sep; aging ends 31 Jul |
| "Returns 1–2%… Brazil South was weather" (Sales Head, Controller) | BR-South returned $12.03M (92% of Brazil, 72% of company); sell-through 0.19 vs 0.39 at 30 Sep 2025, before the drought |
| "Credits out within a month or so" (Controller) | India: 86 days average, 100% late, 88 credits / INR 100.6M still accrued |
| "Pilot territories growth shows it works" | Seasonality artefact |
| Active distributors | 125 / 123 / 115 depending on the definition |

## 3. Method and assumptions
- **As-of date:** 30 Sep 2026. Brazil data ends 21 Sep; Brazil receivables 31 Jul; others 31 Aug. All "FY26" Brazil figures are therefore understated for September, the peak sell-in month.
- **De-duplication:** sell-in by `line_id` (245 repeats), returns by `return_id` (19), credits by `credit_id` (0). Repeats are ERP re-sends of identical rows.
- **Territory:** taken from the distributor master (every distributor books in one territory), not from the transaction code; 1,326 sell-in rows (8.0%) and 83 return rows carried legacy / lower-case / dash-less codes.
- **FX:** monthly average of the published daily rates for the transaction month, per invoice currency (UK = GBP, Canada = CAD). Missing business days (7 per currency, 12 for BRL) are simply not in the average, per Finance policy. USD rate = 1.
- **Net sales (Finance M02):** gross invoiced (invoice date) − negative lines (treated as returns) − returns (return date) − scheme/rebate credits not cancelled (accrual date), USD.
- **Gross sales (Sales Ops M01):** `quantity>0`, order date, local currency; converted only when a total spans currencies.
- **Both definitions are always shown** when a question says "sales", "return rate" or "active distributors"; none is picked silently.
- **Sell-through:** scans ÷ sell-in packs. Scans exist only for enrolled dealers (enrolment 17–100% by territory), so a distributor is compared **only with itself** at the same point last season (`st_rel`).
- **Early-warning backtest:** signal uses only data dated ≤ as-of; outcome = returns after as-of to 30 Jun 2026. Threshold 0.70 is a simple, explainable rule — I did not tune it on outcomes; sensitivity is in the radar tab. It flags 17 of 32 Brazil distributors (53%), so it is a broad alarm that concentrates risk (91% of returns), not a precise predictor of which distributor returns most (rank correlation of st_rel with return rate: −0.55 at 30 Sep, −0.77 at 31 Oct, −0.83 at 30 Nov).
- **Quarter-end loading:** interviews describe it; the data shows only a mild effect (EU 14% and NA 12.7% of sell-in in the last 10 days of a quarter vs 11% if uniform; Brazil none). I did not make it a headline. The incentive-cliff at 90% shows only faint clustering (39 territory-quarters at 90–95% vs 28 at 85–90%).
- **Old-bot permission leak:** counted as territory-manager questions that name another territory code and were answered (358 of 465). Lower bound — questions naming a territory by name were not matched.
- **Voice, chat, meeting join:** mocked. Real versions need: the team-chat app's bot API; a meeting-bot/transcription service; field-app hook; on-device or cloud speech-to-text and text-to-speech in Marathi, Hindi, Telugu, Kannada, Portuguese; cached morning briefs for low-signal areas.

## 4. External research (directional; much of it is vendor-published)
- dbt Labs 2026 benchmark: models answering from a semantic layer scored ~98% vs ~90% on raw SQL; model choice mattered little once definitions were governed.
- Databricks Genie: 53% on bare metadata → 80% with descriptions → 100% only after metric definitions and verified example queries.
- Snowflake: GPT-4o fell to 51% on their internal evaluation set vs benchmark scores near 90%; verified queries + semantic model recover accuracy.
- Industry write-ups on "talk to your data" failures: context fragmentation, metric drift, unverifiable accuracy, no trust infrastructure.
Used as support for the architecture, not as proof of impact — the proof is the replay and backtest above.

## 5. Limitations
- Scan coverage is partial and some dealers batch-scan at month-end; sell-through is a trend signal, not stock.
- No inventory-at-distributor data; return terms (lots, full boxes, deadlines) are not in the data.
- Weather is context, not a modelled driver.
- FY26 targets for Brazil South were raised roughly 9–33% over FY25 (Q4 +9% to +33% by territory) after the regional manager's reported 111% year; baselines from drought seasons should not seed next year's targets without adjustment.
- Translations are template-based and need native-speaker review.
- Incentive design (paying on gross) is a leadership decision; I present evidence only.
