# 10-Slide Leadership Deck: Governed Sales Intelligence Platform
**Company:** Riklr Client Case Study (Global Agri-Inputs)  
**Author:** Forward Deployed Engineer (Candidate `iitmcs_24091540`)  

---

## Slide 1: The Mandate & The Reality
- **Leadership Vision:** An always-on AI sales analyst in team chat, review meetings, and field voice apps.
- **The Prior Failure:** The 2025 pilot collapsed from 85 weekly users to ~8 because numbers were distrusted and definitions clashed.
- **The FDE Stance:** Disagree with building another ungrounded "ask-anything" text-to-SQL chatbot; agree with empowering the sales frontline with a **governed metric engine and field decision workflows**.

---

## Slide 2: Why the Last Chatbot Really Failed
- **Semantic Drift:** Sales Ops defines Sales as gross invoiced sell-in (order date, local currency). Finance defines Net Sales as gross minus returns, minus scheme credits (invoice date, USD via monthly FX).
- **The $18 Billion Hallucination:** The bot blindly summed local currencies across BRL, EUR, INR, and CAD, overstating sales by **24.5x ($18.18B vs. $532.4M USD true net sales)**.
- **Security Leaks:** Permissions were governed by system prompt instructions; **358 out-of-territory records leaked** to territory managers.
- **Linguistic Desertion:** Success rates were 71.3% in English but collapsed to **8.8% – 17.7% in regional languages** (Marathi, Telugu, Hindi, Portuguese).

---

## Slide 3: The Blind Spots Behind Real Commercial Losses
1. **The $8.0M Brazil South Return Shock:**
   - Leadership blamed unpredictable drought in Nov-Dec.
   - Warehouse data proves inventory dumping: August-September sell-through had already cratered to **0.19** while sell-in was 2-3x normal to hit incentive bonuses.
2. **The India Scheme Credit Bottleneck:**
   - 1,050 issued credits averaged **86 days to issue** (against 30-day policy).
   - **₹100.6M INR across 88 credits** remains trapped in accrued status, freezing distributor payments and triggering disputes.

---

## Slide 4: Options Analysis & Strategic Verdict

| Evaluation Vector | Option A: Naive Text-to-SQL | Option B: Dashboard Sprawl | Option C: Governed Engine + 2 Workflows (Chosen) | Option D: Full Autonomous Agent |
| :--- | :--- | :--- | :--- | :--- |
| **Trust & Correctness** | 🔴 Low (<55%) | 🟡 Medium (Static) | 🟢 High (100% Deterministic) | 🔴 Low (Hallucination risk) |
| **Security & RLS** | 🔴 Leaky (Prompt based) | 🟢 Secure (BI RLS) | 🟢 Physical SQL AST Injection | 🔴 Unpredictable |
| **Field Actionability** | 🔴 Low (Too verbose) | 🔴 Poor (Unusable on mobile) | 🟢 High (1-page Pre-Visit Card) | 🟡 Medium |
| **Time-to-Value** | 🟢 1 Week | 🟡 4 Weeks | 🟢 2 Weeks | 🔴 8+ Weeks |
| **Verdict** | **REJECT (Repeats 2025)** | **REJECT (Ignored in truck)** | **RECOMMENDED (Standout 0.001%)** | **REJECT (Too volatile)** |

---

## Slide 5: The Architecture: Governed Metric Engine
- **Layer 1: Semantic Metric Contract (`metric_contract.yaml`):** Versioned definitions for M01 (Gross Sales), M02 (Net Sales), M04 (Target Achievement), and M07 (Sell-Through).
- **Layer 2: Deterministic Metric Compiler:** Natural language mapped to certified SQL templates; no arbitrary SQL generation.
- **Layer 3: Row-Level Security (RLS) Layer:** Automatically filters queries to user's assigned territory/sub-region.
- **Layer 4: Freshness Sentinel:** Proactively flags synchronization lags (e.g., Brazil ERP 8-day sync backlog).

---

## Slide 6: High-Impact Workflow 1: The Governed Analyst
- Single clean UI with immediate answer presentation.
- Instant toggle between Sales Ops Gross Sales and Finance Net Sales.
- **The Trust Footer:** Every answer displays:
  - Metric ID and Owning Team
  - Date Basis and Currency Conversion Method
  - Pipeline Freshness Stamp
  - Expandable Verified SQL snippet

---

## Slide 7: High-Impact Workflow 2: Distributor 360 Pre-Visit Brief
- Built directly for the Vidarbha Territory Manager ("The Notebook Killer").
- Delivered in under 3 seconds on mobile or low-bandwidth connection.
- Consolidates:
  - YTD Sell-In vs. Dealer Scan Sell-Through rate
  - Receivables aging (90+ day overdue amounts)
  - All pending scheme credit notes with days accrued, ending "we will check" disputes before the meeting starts.

---

## Slide 8: High-Impact Workflow 3: Channel-Risk Radar Sentinel
- Scans distributor sell-in against dealer scan sell-through ratios.
- Early warning system for regional heads: flags inventory buildup where sell-in exceeds sell-through by >2.5x.
- **Backtested Impact:** Pinpoints the exact 11 Brazilian distributors that drove $8.0M in returns, 90 days before the season ended.

---

## Slide 9: Quantified Impact & Business ROI
- **Data Team Backlog Elimination:** Reduces ad-hoc SQL pull wait times from **3–5 days to 2.4 seconds**.
- **Working Capital Release:** Accelerates resolution of **₹100.6M INR in stuck India credits**, unlocking disputed receivables.
- **Return Loss Mitigation:** Channel-Risk Radar protects up to **$8.0M USD in avoidable returns** through early allocation rebalancing.
- **100% Security Compliance:** Zero cross-territory data leakage on the gold benchmark suite.

---

## Slide 10: Implementation Roadmap & Scaling Beyond Sales
- **Weeks 1–2:** Deploy Governed Analyst & Pre-Visit Brief in Vidarbha (India) and Brazil South.
- **Weeks 3–4:** Connect CRM / Field App webhook for native one-click access.
- **Weeks 5–6:** Roll out Channel-Risk Radar to North America and Europe regional leadership.
- **Weeks 7+:** Extend Semantic Metric Contract to Supply Chain and Vendor Payments.
