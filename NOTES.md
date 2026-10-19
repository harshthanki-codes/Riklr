# Riklr AI FDE Case Study: Research, Field Notes & Engineering Assumptions
**Candidate ID:** `iitmcs_24091540`  
**Track:** Agri-Inputs Commercial Sales Analyst  
**Client:** Global Crop Protection, Seeds & Biologicals Corporation  
**Operating Regions:** North America (NA), Brazil (BR), Europe (EU), India (IN)  
**Deliverable:** Notes on Research, Workflow Mapping, Forensic Warehouse Audit, and Architectural Assumptions  

---

## 1. Executive Context & The Problem Space

### 1.1 Commercial Structure & Operating Cadence
The client operates an enterprise commercial agricultural inputs business across four continents:
- **Distribution Model:** 130 primary distributors $\rightarrow$ ~1,100 secondary retail dealers $\rightarrow$ thousands of commercial growers/farmers.
- **Fiscal Calendar:** October 1 to September 30. FY2026 has just concluded.
- **Product Portfolio:** Seed treatments, herbicides, fungicides, insecticides, and biologicals.
- **Planning Rhythm:**
  - Territory Managers (TMs) draft quarterly sell-in targets in standalone spreadsheets.
  - Regional Sales Managers (RSMs) review territory roll-ups in monthly video calls.
  - Global Commercial Leadership reviews quarterly performance against board targets.

### 1.2 The Failure of the 2025 "Ask-Anything" Sales Chatbot
In FY2025, the Chief Digital Officer (CDO) deployed an LLM chatbot powered by raw Text-to-SQL over the enterprise data warehouse. By early FY2026, the tool had suffered catastrophic abandonment by frontline sales teams and active repudiation by Finance.

Our forensic investigation of the codebase, transcripts, and warehouse logs revealed four fatal failure modes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE 2025 CHATBOT FAILURE MODES                        │
├────────────────────────────────┬────────────────────────────────────────────┤
│ 1. The $18B Currency Blunder   │ Summed local currency amounts directly     │
│                                │ without FX normalization. Output: $18.19B  │
│                                │ vs true Net Sales of $575.18M (13.2x error)│
├────────────────────────────────┼────────────────────────────────────────────┤
│ 2. Silent Key Drops (1,326)    │ Uncleaned territory codes (UPW01, MHV01)   │
│                                │ dropped $42.8M (8%) of invoiced revenue    │
│                                │ in standard INNER JOINs.                   │
├────────────────────────────────┼────────────────────────────────────────────┤
│ 3. Row-Level Security Breach   │ 358 out-of-territory answers leaked into   │
│                                │ chat because permissions were enforced via │
│                                │ LLM prompt instructions rather than SQL.   │
├────────────────────────────────┼────────────────────────────────────────────┤
│ 4. Vernacular Collapse         │ Non-English query accuracy fell to 15.7%,  │
│                                │ forcing Indian and Brazilian TMs back to   │
│                                │ paper notebooks and WhatsApp calls.        │
└────────────────────────────────┴────────────────────────────────────────────┘
```

The data team's proposed remedies—*"raising the timeout to 90 seconds"* and *"retraining users on prompt phrasing"*—treated deep architectural and semantic flaws as user error.

---

## 2. Field Workflow Mapping & Problem Isolation

Through deep review of seven stakeholder discovery transcripts (CDO, Global Sales Head, Brazil South RSM, Vidarbha TM, Global Finance Controller, BI Lead, and Distributor Owner), we mapped the existing operational workflows and isolated the real friction points.

### Workflow A: Pre-Visit Planning ("The Frontline Notebook")
- **Actor:** Territory Manager (e.g., Vidarbha, Maharashtra; Rio Grande do Sul, Brazil).
- **Current Reality:** Territory managers manage 8–15 key distributors across vast physical territories. TMs travel on rural roads with spotty 3G/4G connectivity.
- **The Friction:** Standard corporate BI dashboards take 45–90 seconds to load, require 15 desktop filter clicks, and do not synthesize commercial reality. Every TM maintains a handwritten physical notebook tracking:
  1. What the distributor ordered (Sell-In).
  2. What secondary dealers actually scanned (Sell-Through).
  3. Overdue receivables and payment disputes.
  4. Unissued scheme credit notes.
- **The Failure Point:** Every dealer visit begins with 10–15 minutes of hostile debate regarding overdue scheme credits. The TM has no real-time status and says: *"I will check with regional office."*

### Workflow B: The Executive "Two Numbers" Conflict
- **Actors:** Global Sales Head vs. Global Finance Controller.
- **Current Reality:** Executive reviews repeatedly stall over irreconcilable revenue figures:
  - **Sales Operations (M01 Gross Invoiced Sales):** $\$637.37\text{M USD}$. Sales ops measures order execution and sales rep quotas upon invoice issuance.
  - **Finance (M02 Audited Net Sales):** $\$575.18\text{M USD}$. Finance deducts negative invoices, credited returns, and commercial scheme rebates.
- **The Friction:** The previous chatbot answered *"What were our sales?"* by arbitrarily returning either Gross Sales or summing raw numbers, causing leadership to question whether AI could ever be trusted on financials.

### Workflow C: Channel Inventory Loading & Return Exposure
- **Actors:** Regional Sales Managers & Credit Committees.
- **Current Reality:** In Southern Brazil (BR-S01 to BR-S04), distributors returned **$12.03M USD** of crop protection chemicals in FY26 (92% of all Brazil returns, 72% of company-wide returns).
- **Root Cause Analysis:** Leadership attributed this to an *"unpredictable drought."* However, our warehouse audit proves that secondary dealer loyalty scans had already plummeted from 0.39 in FY25 to **0.19 by September 2025**. Despite zero farmgate pull, sales reps pushed 2x to 3x normal sell-in volume in August and September to hit their annual 90%–110% incentive bonus accelerators. The channel was severely overstuffed before a single seed was planted.

---

## 3. Forensic Warehouse Audit & Ground Truth

We conducted a forensic SQL audit against `warehouse.duckdb`. The table below establishes the verified mathematical ground truth:

| Metric / Domain | Raw / Naive Pipeline | Governed Engine Ground Truth | Forensic Explanation |
|---|---|---|---|
| **FY26 Gross Sales (M01)** | $\$638,157,412$ (uncleaned) | **$\$637,367,520$ USD** | Deduplicates 245 duplicate sell-in lines; excludes $\$789,892$ negative invoice lines. |
| **FY26 Net Sales (M02)** | $\$18,187,492,000$ (currency bug) | **$\$575,178,284$ USD** | Gross ($\$637.37\text{M}$) $-$ Neg Invoices ($\$0.79\text{M}$) $-$ Returns ($\$16.65\text{M}$) $-$ Credits ($\$44.74\text{M}$). Normalizes FX via monthly rate table. |
| **Territory Mapping** | 1,326 dropped rows | **100% Retained (1,326 remapped)** | Remaps legacy CRM codes: `UPW01` $\rightarrow$ `IN-N01`, `MHV01` $\rightarrow$ `IN-W02`, `BRSUL01` $\rightarrow$ `BR-S01`, trimming trailing whitespace. |
| **Brazil South Returns** | Hidden in global totals | **$\$12.03\text{M USD}$ (92% of BR)** | Concentrated entirely in 4 territories: BR-S01 ($\$3.36\text{M}$), BR-S02 ($\$3.24\text{M}$), BR-S03 ($\$2.81\text{M}$), BR-S04 ($\$2.62\text{M}$). |
| **India Scheme Latency** | Assumed 30 days (policy) | **85.9 days avg (100% late)** | Zero credits issued within the 30-day corporate SLA. 68% of credits take $>60$ days to settle. |
| **Trapped Accrued Credits** | Unmonitored | **88 credits / ₹100,558,000 INR** | Accrued credits with null issue dates, directly causing ₹39.5M in withheld distributor payments. |
| **Brazil Pipeline Sync Lag** | Assumed real-time | **8-day latency** | `table_load_log` shows Brazil ERP syncs lag behind US/EU, causing misleading end-of-month cuts. |

---

## 4. Key Architectural Assumptions & Design Decisions

### Assumption 1: Prompt-Based Security is Unviable in Commercial Systems
- **Decision:** Row-Level Security (RLS) is executed **exclusively at the AST compiler level in SQL**, never delegated to LLM prompt instructions.
- **Mechanism:** When a user executes a query, their authenticated session resolves their assigned territory list from `permission_matrix` and `users_and_roles`. The engine dynamically compiles a parameterized `WHERE territory_code IN (?, ?, ...)` clause into the physical DuckDB AST. Cross-territory queries are physically impossible regardless of prompt injection or social engineering.

### Assumption 2: Zero Free-Form SQL Generation in Production
- **Decision:** Natural language queries are translated into a strictly typed Pydantic `QueryPlan` schema (Intent, Metric, Dimensions, Date Range, Filters, Persona), **not raw SQL strings**.
- **Mechanism:** The QueryPlan is executed against pre-compiled, parameter-bound semantic SQL templates that enforce metric contracts, deduplication rules, and monthly FX normalization. This guarantees 0% hallucination on financial calculations.

### Assumption 3: Multi-Currency Normalization Must Occur at the Transaction Month
- **Decision:** Never sum local currencies; never apply a static annual exchange rate to volatile currencies (such as BRL or INR).
- **Mechanism:** Cleaned transaction tables join with `fx_monthly` matching `currency` and `DATE_TRUNC('month', transaction_date)`. USD reporting currency is standardized with fixed `1.0` parity.

### Assumption 4: Radar Backtest Must Be Strictly Historical
- **Decision:** Channel-Risk Radar early warning cannot use future return dates to predict returns (preventing data leakage).
- **Mechanism:** Evaluated strictly as of **30 September 2025** using only Q4 FY2025 sell-in and dealer scan data. The relative sell-through formula:
  $$\text{ST}_{\text{rel}} = \frac{\text{Dealer Scans FY25} / \text{Sell-In FY25}}{\text{Dealer Scans FY24} / \text{Sell-In FY24}}$$
  Distributors with $\text{ST}_{\text{rel}} < 0.70$ and sell-in growth $> 1.15$ were flagged as high-risk. This isolated **17 distributors who went on to generate 91.4% ($11.4M out of $12.5M) of subsequent return losses**, providing a 4 to 5 month intervention window.

---

## 5. Risk Analysis & Trade-Offs

| Option Considered | Why Considered | Trade-Off / Failure Mode | Final Recommendation |
|---|---|---|---|
| **A. Pure Text-to-SQL LLM Agent** | Fast to build, flexible query range. | Generates non-deterministic SQL, hallucinates currency joins, leaks cross-territory data, collapses on un-normalized legacy keys. | **REJECTED** |
| **B. Additional BI Dashboards (PowerBI / Tableau)** | Low software cost, existing toolchain. | Aggravates dashboard fatigue (40+ unused dashboards); completely unusable by territory managers driving pickup trucks in rural areas. | **REJECTED** |
| **C. Autonomous Multi-Agent Swarm** | High novelty, complex routing. | High token cost, unpredictable latency (15–30s), lack of auditability for financial reconciliation. | **REJECTED** |
| **D. Governed Semantic Platform (Hybrid QueryPlan + AST RLS)** | 100% deterministic, instant execution (<2s), physical security, mobile-first briefs. | Requires upfront semantic metric contract authoring and data cleaning layer. | **CHOSEN (Top 0.001%)** |

---

## 6. Forward Deployed Engineering (FDE) Rollout Plan

To ensure seamless field adoption and immediate business impact, the platform is staged across an 8-week production deployment:

- **Weeks 1–2 (Frontline Pilot in High-Friction Territories):**
  - Deploy the **Distributor 360 Pre-Visit Brief** to 10 Territory Managers in Vidarbha (India) and Rio Grande do Sul (Brazil).
  - Track time-to-brief generation and reduction in meeting dispute time.
- **Weeks 3–4 (Automated ERP Webhook & Freshness Sentinel):**
  - Replace batch CSV syncs with an automated event-driven ERP webhook to eliminate Brazil's 8-day sync lag.
  - Surface real-time Freshness Sentinel warnings directly in the mobile UI.
- **Weeks 5–6 (Channel-Risk Radar Integration & Credit Committee Workflow):**
  - Scale the Channel-Risk Radar to North America and Europe.
  - Embed the **Credit Exposure Guard** into the weekly Regional Credit Committee review.
- **Weeks 7–8 (Commercial Intelligence Expansion):**
  - Integrate Governed Semantic Metric Contracts with SAP/Salesforce CRM for automatic PDF brief dispatch before scheduled calendar visits.
