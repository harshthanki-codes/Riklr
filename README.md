# Riklr AI FDE Case Study: Governed Commercial Sales Intelligence Platform
**Candidate ID:** `iitmcs_24091540`  
**Track:** Agri-Inputs Commercial Sales Analyst  
**Client:** Global Crop Protection, Seeds & Biologicals Corporation (North America, Brazil, Europe, India)  
**Assessed By:** Riklr Forward Deployed Engineering Evaluation Committee  
**GitHub Collaborator Invited:** `rr-riklr`  
**Video Walkthrough (Google Drive):** [https://drive.google.com/file/d/1HHB5vycICn5DXzOQ2WfLMxMBebHzAPXg/view?usp=drive_link](https://drive.google.com/file/d/1HHB5vycICn5DXzOQ2WfLMxMBebHzAPXg/view?usp=drive_link)  

---

## 1. Executive Summary & Root Cause Thesis

Last year's enterprise sales chatbot failed not because large language models are incapable of arithmetic, but because the system suffered from **semantic drift, unhandled multi-currency conversions, missing Row-Level Security (RLS), and zero data pipeline freshness awareness**.

Instead of diagnosing these architectural flaws, the data team blamed users and attempted to patch the tool by increasing query timeouts and offering prompt re-phrasing classes. Frontline sales representatives responded by abandoning the tool and returning to handwritten paper notebooks and phone calls.

### Forensic Ground Truth from the Data Warehouse (`warehouse.duckdb`)

| Dimension / Domain | 2025 Naive Chatbot | Governed Engine (Ground Truth) | Engineering Impact |
|---|---|---|---|
| **FY26 Net Sales (M02)** | $\$18,187,492,000$ (currency bug) | **$\$575,178,068$ USD** | The naive bot summed local currency invoices (BRL, EUR, INR, CAD) directly without FX conversion, producing a **13.2x like-for-like hallucination**. |
| **FY26 Gross Invoices (M01)** | $\$638,157,412$ (uncleaned) | **$\$637,367,520$ USD** | Purges 245 duplicate sell-in lines and isolates $\$789,892$ negative invoice lines. |
| **Territory Mapping** | 1,326 rows dropped ($42.8M) | **100% Retained (1,326 remapped)** | Remaps legacy CRM codes (`UPW01` $\rightarrow$ `IN-N01`, `MHV01` $\rightarrow$ `IN-W02`, `BRSUL01` $\rightarrow$ `BR-S01`) and strips trailing whitespace. |
| **Brazil South Returns** | Hidden in global totals | **$\$12.03\text{M USD}$ (92% of BR)** | 4 territories (BR-S01 to BR-S04) drove 72.2% of all company returns. Dealer scan sell-through collapsed to 0.19 by September while reps dumped inventory to hit incentive accelerators. |
| **India Scheme Latency** | Assumed 30 days (policy) | **85.9 days avg (100% late)** | Zero credits met the 30-day SLA; 68% took $>60$ days. **88 credits totaling ₹100.6M INR** are stuck in `Accrued` status, creating ₹39.5M in withheld distributor payments. |
| **Row-Level Security** | 358 out-of-territory leaks | **Zero Data Leaks (100% AST RLS)** | Prompt-only role security replaced with physical SQL AST injection (`WHERE territory_code IN (...)`). |
| **Pipeline Freshness** | Assumed real-time | **8-day Brazil lag flagged** | Dynamically checks `table_load_log` to warn users when transaction batches are delayed. |

---

## 2. Submission Deliverables Index

Per the formal requirements in `Riklr-FDE-Case-Study.pdf`, the complete submission package contains:

| Deliverable | Location in Repo | Description |
|---|---|---|
| **1. Code Prototype** | [`src/`](file:///c:/Users/Admin/Desktop/Riklr/src) & [`src/ui/app.py`](file:///c:/Users/Admin/Desktop/Riklr/src/ui/app.py) | Enterprise 5-tab dark slate Streamlit platform (Governed Analyst, Waterfall Bridge, Distributor 360 Brief, Channel Radar, Credit Guard). |
| **2. Notes on Research & Assumptions** | [`NOTES.md`](file:///c:/Users/Admin/Desktop/Riklr/NOTES.md) | Deep stakeholder analysis, workflow mapping, forensic warehouse audit, mathematical proofs, and FDE rollout roadmap. |
| **3. Executive Deck (10 Slides)** | [`Riklr_Sales_Analyst_Deck.pptx`](file:///c:/Users/Admin/Desktop/Riklr/Riklr_Sales_Analyst_Deck.pptx) & [`.pdf`](file:///c:/Users/Admin/Desktop/Riklr/Riklr_Sales_Analyst_Deck.pdf) | McKinsey/Palantir-style 16:9 executive presentation in both PowerPoint and PDF formats (strictly 10 slides). |
| **4. Coding Harness & Prompts** | [`chat-history/PROMPTS.md`](file:///c:/Users/Admin/Desktop/Riklr/chat-history/PROMPTS.md) & [`session_transcript.jsonl`](file:///c:/Users/Admin/Desktop/Riklr/chat-history/session_transcript.jsonl) | Senior Prompt Harness Engineer documentation, system prompts, few-shot contracts, and 50-Prompt Gold Standard Evaluation Suite. |
| **5. Narrated Video Walkthrough** | [Google Drive Stream Link](https://drive.google.com/file/d/1HHB5vycICn5DXzOQ2WfLMxMBebHzAPXg/view?usp=drive_link) & [`walkthrough.mp4`](walkthrough.mp4) | Narrated live video demo walking through problem context, isolated workflows, and the working prototype. |

---

## 3. Governed Semantic Architecture

```
[ Frontline User Query: English / Portuguese / Romanized Hindi / Romanized Marathi ]
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   Semantic Router Contract   │  <-- Translates intent to typed
                     │  (Pydantic QueryPlan Schema) │      QueryPlan JSON (No raw SQL)
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   Physical AST RLS Injector  │  <-- Injects physical WHERE
                     │  (Users & Permission Matrix) │      territory_code IN (...)
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Materialized Cleaning Layer │  <-- Remaps 1,326 legacy keys,
                     │ (DuckDB Temp Tables + Dedupe)│      purges 245 duplicates
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Dynamic Monthly FX Engine   │  <-- Converts BRL, EUR, INR, CAD
                     │ (fx_monthly Table Join)      │      to standardized USD
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Freshness Sentinel Guard    │  <-- Checks max business date &
                     │ (Monitors table_load_log)    │      flags 8-day Brazil sync lag
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Verified Trust Footer Emit  │  <-- Metric ID, Owner, Basis,
                     │  (Complete Audit Trail)      │      and Compiled Parameterized SQL
                     └──────────────────────────────┘
```

---

## 4. High-Impact Workflows Delivered

### Workflow 1: Governed Multilingual Analyst & Two Numbers Waterfall Bridge
- Resolves executive tension between Sales Ops ($637.4M Gross) and Finance ($575.2M Net) with a live 5-step waterfall reconciliation.
- Multilingual voice/text support across English, Brazilian Portuguese, and Romanized Hindi/Marathi (e.g., *"Tiranex Agro Agencies chi baki kiti aahe?"*).
- Physical Row-Level Security guarantees zero cross-territory data leakage.

### Workflow 2: Distributor 360 Pre-Visit Brief ("The Notebook Killer")
- Replaces the territory manager's physical notebook with a mobile-optimized one-page card generated in under 2 seconds.
- Displays Sell-In vs. Dealer Scan Sell-Through rate, 90+ day overdue receivables, and all accrued scheme credits with aging compared against regional benchmarks (India median: 78 days).
- Automatically redacts monetary margins for Field Agronomists while maintaining product volume data.

### Workflow 3: Channel-Risk Radar Sentinel
- Scans distributor sell-in volumes against secondary dealer loyalty scans.
- Strictly historical backtest as of September 30, 2025: **flagged 17 distributors who accounted for 91.4% ($11.4M out of $12.5M) of subsequent return losses in Brazil South**, giving management 4 to 5 months of advance notice to rebalance stock.

### Workflow 4: Working Capital & Credit Exposure Guard
- Detects accounts operating at 200% to 350% credit limit utilization (e.g., Modorar Seeds operating at 330% limit).
- Pinpoints ₹39.5M INR in disputed receivables tied directly to unissued scheme credits, accelerating settlement and unlocking commercial cash flow.

---

## 5. Narrated Video Walkthrough

The complete narrated walkthrough demonstrating the problem context, isolated workflows, and live working prototype is available via:
- **Instant Cloud Streaming (Recommended):** [Watch Narrated Prototype Walkthrough on Google Drive](https://drive.google.com/file/d/1HHB5vycICn5DXzOQ2WfLMxMBebHzAPXg/view?usp=drive_link) *(Permission: Anyone with the link can view)*
- **Direct Video File in Repository:** [`walkthrough.mp4`](walkthrough.mp4) (46.4 MB — committed directly in repo root)
- **Narrated Script Document:** [`script riklr.pdf`](file:///c:/Users/Admin/Desktop/script%20riklr.pdf) (Word-for-word cue sheet on Desktop)

---

## 6. Reproduction & Run Steps

### Prerequisites
- Python 3.10+
- OS: Windows, macOS, or Linux

### Step 1: Clone the Repository
```bash
git clone https://github.com/harshthanki-codes/Riklr.git
cd Riklr
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Verification Test Suite
Executes the physical AST RLS tests, net sales reconciliation, pre-visit brief generation, and Channel-Risk Radar backtest:
```bash
python tests/run_all_tests.py
```
*Expected Output: `SUCCESS: ALL VERIFICATION CHECKS PASSED (100% GREEN)`*

### Step 4: Launch the Interactive Streamlit Web Platform
```bash
streamlit run src/ui/app.py
```
Open your browser to `http://localhost:8501` to interact with:
1. **Governed Analyst:** Multilingual queries with trust footers and role-switching.
2. **Waterfall Bridge:** Live Gross-to-Net Sales financial reconciliation.
3. **Distributor 360 Brief:** 1-page pre-visit brief for territory managers.
4. **Channel-Risk Radar:** Early warning inventory scan and verified backtest.
5. **Credit Guard:** Credit limit overdraft monitor and disputed receivables.

### Step 5: (Optional) Rebuild the 10-Slide Presentation Deck
```bash
python src/engine/build_deck.py
```
Regenerates `Riklr_Sales_Analyst_Deck.pptx` and `Riklr_Sales_Analyst_Deck.pdf` directly in the project root.

---

## 7. Submission Checklist & Integrity Confirmation

- [x] Private GitHub repository with collaborator `rr-riklr` invited.
- [x] Working prototype with tested reproduction steps in `README.md`.
- [x] Notes on research, assumptions, and workflow mapping in `NOTES.md`.
- [x] 10-slide executive presentation deck available as both `Riklr_Sales_Analyst_Deck.pptx` and `Riklr_Sales_Analyst_Deck.pdf`.
- [x] Complete coding harness transcript and prompt evaluation suite in `chat-history/`.
- [x] Dedicated 4-minute narrated video walkthrough link.
- [x] All numbers mathematically reconciled against `warehouse.duckdb`.
