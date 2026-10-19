# 02 — 10-slide deck (export as PDF → docs/deck.pdf)

Story arc the brief asks for: **problem & context → workflows → options → solution → impact**.
Design rule ("taste"): one idea per slide, one chart or table, ≤ 35 words of body text, big numbers, no emoji, one accent colour (the charts use #d1495b on grey).
Every number below prints from `scripts/verify_headlines.py`. Anything marked ▲ is a screenshot to take from the running app.

---

## Slide 1 — Verdict
**Title:** Don't build "ask anything". Build the number people can trust.
**Body (3 big stats):** 13× — the old bot's global total was that overstated, like for like · 85 → 8 — weekly users, peak to today · $12.0M — returned from one sub-region nobody saw coming
**Line under:** We agree with the need (an analyst the field can use). We disagree with the plan (a model on raw tables, measured by usage).
**Notes:** Open with the position. The CDO asked us to agree or disagree; say which, in one sentence.

## Slide 2 — How the team plans and decides today (workflow map)
**Visual:** left-to-right flow: Sales Ops target (gross, local) → Territory manager spreadsheet → Monthly regional review (dashboard on screen) → Finance net sales (USD, after month-end) → Quarter-end push. Underneath, a second lane: *what actually happens* — notebooks, messaging-app photos, Monday calls, voice notes to a BI analyst's personal phone, 30–40 ad-hoc requests/week to BI.
**Red marks at 4 breaks:** (1) two definitions, two numbers; (2) nobody sees sell-out, only sell-in; (3) credits and overdue arrive by email once a month; (4) field works in Marathi/Portuguese, tools are English.
**Notes:** Name the sources: 7 interviews, call notes, load log, 9,232 old-bot questions.

## Slide 3 — Why the 2025 bot really died (evidence, not opinion)
**Visual:** 4 evidence tiles.
- Summed BRL + INR + EUR + USD: **$8.40B vs $637M** true gross FY26 (13×).
- Answered **71%** of English questions, **16%** of every other language (Marathi 18%, Hindi 16%, Portuguese 16%).
- One service account, no row filters: **358 answers** to territory managers asking about other territories.
- Peak **85** users/week (not "hundreds") → **8** today.
**Notes:** Quote the BI Lead: "a currency table and a rule would catch it every time." A better model does not fix a missing rule.

## Slide 4 — The "+62% pilot uplift" was the calendar
**Visual:** `chart1_pilot_illusion.png`.
**Title:** Pilot territories "grew 62%". They'd have grown 55% with no bot at all.
**Body:** India's kharif quarter is in the pilot. Same comparison in 2026, no bot: pilot +55%, others −45%. The Sales Head said this in the corridor; the data agrees. So the proposed "half the territories" test would fail the same way.
**Design we recommend instead:** pair territories within the same region and season; compare against the same quarter last year; judge on accuracy, leakage, tickets to BI, credit lag — not on sell-in growth.

## Slide 5 — Problem 1: nobody can say which number is right
**Visual ▲:** the "Two numbers, one bridge" waterfall: Sales Ops gross → USD → date basis → − returns → − credits = Finance net.
**Body:** FY26 clean: gross $637M → net **$575M** (returns $16.7M, scheme credits $44.7M). Data traps fixed in code: 245 duplicate lines, 1,326 rows with legacy territory codes (8% of sell-in), 58 negative lines, FX gaps. Brazil data stops 21 Sep: **15 of 52 loads since 10 Aug succeeded**; the receivables snapshot is from 31 Jul.
**Notes:** Finding framed as a handover to the BI team (she asked to hear it before the CDO).

## Slide 6 — Problem 2a: Brazil South — loaded, not sold
**Visual:** `chart2_brazil_south_sellthrough.png`.
**Title:** The warning was visible two months before the drought.
**Body:** Returns **$12.0M** = 92% of Brazil, 72% of the company. Sell-through was **0.19 vs 0.39** last season at 30 Sep 2025, while September sell-in was 1.4–3.2× the previous September (3.2× in BR-S01). **Backtest, using only data available on 30 Sep 2025:** 17 of 32 distributors flagged hold **91% ($11.4M of $12.5M)** of later returns; 15 of the 17 are top returners. The drought made it worse; it didn't start it.
**Notes:** Be fair: weather is real (rain 40% of normal Nov–Dec). Say "scans cover enrolled dealers only, so we compare each distributor with itself."

## Slide 7 — Problem 2b: India — credits that never arrive
**Visual:** `chart3_india_credit_lag.png`.
**Body:** 86 days average vs a 30-day policy; every issued credit was late; **88 credits / INR 100.6M still accrued**. Distributors hold payment until credits arrive, which shows up as "overdue"; finance had flagged only part of it as disputed. The territory manager hears it "in the first ten minutes of every visit."
**Notes:** Quote the Vidarbha TM: "I don't need a robot. I need the page — like my notebook, but correct."

## Slide 8 — Options compared
| | A. Ask-anything on raw tables | B. More dashboards | **C. Governed analyst + 2 workflows** | D. Autonomous agent |
|---|---|---|---|---|
| Correct numbers | ✗ repeats 13× error | ✓ static | ✓ one definition, shown | ? unbounded |
| Permissions | ✗ service account | ✓ BI filters | ✓ enforced in data layer | ? |
| Helps in the truck | ✗ | ✗ 40 already | ✓ one page, local language | ~ |
| Time to value | fast | slow | days (prototype running) | months |
| **Measured on the 60-question set** | *fill from eval_results* | n/a | *fill from eval_results* | n/a |
**Verdict:** C. Also rejected: tying incentives to following AI advice (the field already feels watched).
**Notes:** Fill the measured row only from `docs/eval_results.md`.

## Slide 9 — The solution (what runs today)
**Visual ▲:** 3 screenshots: Ask (answer + trust chips) · Distributor brief in Marathi · Radar with as-of slider.
**Architecture strip (one line):** question (typed or voice) → plan (closed menu, no SQL from a model) → permission gate → metric engine (cleaned data, FX) → freshness check → answer + audit log.
**Body:** Definitions in code; permissions enforced before any query; stale or unknown → "I can't answer that reliably."
**Notes:** Mention what is mocked (chat tool, meeting join, field app, speech) and what the real integration needs.

## Slide 10 — Impact, proof, and what we'd do next
**Left: impact in numbers (all measured):**
- 13× overstatement removed; net matches Finance's definition.
- 0 cross-territory answers vs 358 in the old log (replay).
- Non-English answered: **x% vs 16%** *(from replay)*.
- Exposure addressed: up to **$11.4M** of the **$12.5M** later returns sat with distributors flagged at 30 Sep.
- INR **100.6M** of pending credits made visible per distributor.
**Right: how we'd prove it in the field:** matched territory pairs, same-season year-on-year, leading indicators first.
**Next:** (1) agree one definition owner per metric; (2) fix Brazil loads; (3) pilot with Vidarbha and Brazil South managers; (4) incentive review is a leadership decision — we bring evidence only.
**Notes:** End on the ask: three decisions (definition owners, Brazil loads, pilot sites).
