# RESEARCH & ASSUMPTIONS NOTES
**Case Study:** Global Agri-Inputs Commercial Sales Intelligence Platform  
**Candidate ID:** `iitmcs_24091540`  
**Role:** AI Forward Deployed Engineer (AI FDE)  
**Date of Submission:** Monday, 19 October 2026  

---

## 1. Problem Diagnosis & Evidence Breakdown

### The Surface Perception vs. The Ground Reality
Leadership believed that sales planning in spreadsheets was simply slow and that an "ask-anything" conversational AI assistant deployed to team chat and mobile apps would eliminate the BI team's ad-hoc ticket backlog. The previous year's sales chatbot had already failed in production, collapsing from 85 weekly users to ~8.

Through systematic audit of `warehouse.duckdb` and the 7 discovery interview transcripts, we isolated the actual core failures:

1. **The Semantic & Currency Trap (Why AI Failed)**:
   - **Sales Operations Definition (M01)**: Gross sell-in invoiced to distributors, measured by `order_date`, in local currency without deductions.
   - **Finance Reporting Definition (M02)**: Net Sales = Gross Sales minus Returns minus Scheme/Rebate Credits minus Negative Invoices, measured by `invoice_date`, converted to USD using transaction monthly average exchange rates (`fx_rates`).
   - **The $18 Billion Hallucination**: When the previous bot was asked for "total sales", it generated `SELECT SUM(invoice_amount_local) FROM sell_in_orders`, summing BRL, EUR, CAD, and INR numbers directly. This yielded **$18,188,495,311.96** across the full dataset—a **24.54x overstatement** against the 1-year net sales figure ($532M–$575M) and a **13x overstatement** like-for-like.

2. **The Dirty Warehouse Baseline (Dropped Rows & Legacy Keys)**:
   - **1,326 transaction rows** carried un-normalized territory codes:
     - 631 rows carried pre-2023 legacy CRM codes (e.g. `UPW01` -> `IN-N03`, `MHV01` -> `IN-W01`, `BRSUL01` -> `BR-S01`, `GBR` -> `EU-UK1`).
     - 695 rows carried trailing whitespace or lowercase codes (e.g., `'BR-S01 '`, `'na-p01'`).
   - A naive join (`INNER JOIN territories t ON s.territory_code = t.territory_code`) silently dropped ~8% of commercial sales volume ($42.8M USD).
   - **245 duplicate line items** existed across `sell_in_orders`.
   - Normalizing territory codes via `UPPER(TRIM(territory_code))` and mapping to `legacy_code` restores full ledger reconciliation to **~$575.2M USD**.

3. **The Brazil South $8.0M Return Debacle**:
   - In FY2026, Southern Brazil (BR-S01 to BR-S04) returned **$8,004,472 USD** out of $8.85M total Brazilian returns (**90.4%** of the region's returns).
   - While regional leadership attributed this to late drought in Nov-Dec, warehouse scan records reveal that **dealer scan sell-through had already dropped to 0.19** in Aug-Sep (vs. 0.39 the prior season). Territory managers loaded distributors with 2–3x normal volume at quarter-end to secure 90-110% incentive achievement.

4. **The India Scheme Credit Bottleneck**:
   - 1,050 issued credits took an average of **85.94 days to issue** against a 30-day policy (68% took over 60 days).
   - **₹100,558,000 INR across 88 credits** remained trapped in `Accrued` status with zero issue date. Distributors withheld payments against unissued credits, driving ₹39.5M in flagged disputes and stalling receivables collections.

5. **Security & Linguistic Desertion**:
   - The previous bot enforced data permissions via system prompt instructions, resulting in **358 out-of-territory records leaked** to territory managers.
   - Bot query completion fell from **71.3% in English** down to **8.8% – 17.7% in regional languages** (Marathi 17.7%, Telugu 15.6%, Hindi 15.7%, Punjabi 8.8%), causing field reps to abandon the tool and revert to paper notebooks.

---

## 2. Solution Comparison & Strategic Tradeoffs

| Option | Architecture | Correctness & Trust | Security / RLS | Field Adoption | FDE Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A** | Raw Text-to-SQL on Warehouse | 🔴 Catastrophic (<52% accuracy, currency traps) | 🔴 Leaky (Prompt based) | 🔴 Abandoned (No offline/field fit) | **REJECT**: Repeats 2025 pilot disaster. |
| **Option B** | Additional BI Dashboards | 🟡 Static (Cannot answer ad-hoc questions) | 🟢 Secure (Native BI RLS) | 🔴 Low (Unusable in truck/village) | **REJECT**: Adds to the 40 unused dashboards. |
| **Option C** | **Governed Metric Engine + 2 Field Workflows** | 🟢 100% Deterministic (Verified Metric Contract) | 🟢 Physical SQL AST Injection | 🟢 High (1-page Mobile Brief + Radar) | **CHOSEN**: Solves trust, security, and field utility. |
| **Option D** | Fully Autonomous Multi-Agent | 🔴 Unpredictable (Complex multi-agent loops) | 🟡 Inconsistent | 🔴 High latency, low bandwidth failure | **REJECT**: Excessive overhead for field planning. |

---

## 3. High-Impact Workflows Built

1. **Governed Analyst (Trust-First Querying)**:
   - Version-controlled Semantic Metric Contract (`metric_contract.yaml`).
   - Clean UI showing definitions, date basis, currency basis, pipeline freshness warnings, and compiled SQL.
   - Physical Row-Level Security ensuring zero cross-territory data leakage.

2. **Distributor 360 Pre-Visit Brief ("The Notebook Killer")**:
   - Single-page operational card designed for territory managers before distributor meetings.
   - Displays sell-in vs. scan sell-through, receivables aging (90+ days), and aged pending scheme credits.
   - Multilingual support for field accessibility (English, Marathi, Hindi, Portuguese).

3. **Channel-Risk Radar Sentinel**:
   - Compares distributor sell-in against end-grower scan sell-through ratios.
   - Provides a 90-day early warning before products are trucked back as returns.

---

## 4. Key Assumptions & Modeling Decisions
- **Fiscal Calendar**: FY runs October 1 to September 30. FY2026 = 2025-10-01 to 2026-09-30.
- **FX Normalization**: Transactions convert to USD at the monthly average rate of the transaction month using business-day rates from `fx_rates`.
- **Territory Cleansing**: All legacy CRM codes map to active territories; whitespace and case variations are normalized.
- **Deduplication**: Distinct `order_id` + `line_id` used for unique invoice lines.
