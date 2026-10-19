# Riklr AI FDE Case Study: Governed Sales Intelligence Platform
**Candidate ID:** `iitmcs_24091540`  
**Role:** Forward Deployed Engineer (FDE)  
**Submission Package:** Code Prototype, Research & Assumptions Notes, 10-Slide Deck, Evaluation Harness

---

## 1. Executive Summary & Thesis
Last year's "Ask-Anything" sales chatbot failed not because LLM models were weak, but due to **semantic drift, unhandled multi-currency conversions, missing Row-Level Security (RLS), and zero pipeline freshness awareness**.

### The Forensic Evidence from the Warehouse:
1. **The 24.5x Currency Blunder:** Naive summing of local currencies produced **$18.18 Billion** against a true net sales figure of **$532.39M USD**, because the bot summed BRL, EUR, CAD, and INR numbers directly without daily/monthly FX conversion.
2. **The Brazil South $8.0M Disaster:** 90.4% ($8.0M out of $8.85M) of all Brazilian returns occurred in Southern Brazil (BR-S01 to BR-S04). Territory managers pushed massive sell-in orders in Aug-Sep to hit 90-110% incentive targets while dealer scans had collapsed to 0.19.
3. **The India Scheme Credit Impasse:** 1,050 issued credits averaged **85.9 days to issue** (vs. 30-day policy). **₹100,558,000 INR across 88 credits** are stuck in `Accrued` status, sparking distributor payment disputes and blocking collections.
4. **Security Leakage:** Over **358 out-of-territory queries leaked** across regional sales reps in the previous bot because permissions were handled via prompt instructions rather than physical SQL row filters.
5. **Language Abandonment:** Success rates in regional field languages dropped to **8.8% – 17.7%** (Marathi 17.7%, Telugu 15.6%, Hindi 15.7%, Punjabi 8.8%), forcing field sales reps back to paper notebooks and phone photos.

---

## 2. Architecture: Governed Metric Engine vs. Naive Chatbot

```
[ Natural Language / Voice / UI Query ]
                  │
                  ▼
   ┌──────────────────────────────┐
   │  Semantic Metric Contract    │  <-- Version-controlled metric definitions
   │  (M01 Gross vs M02 Net)      │
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  Physical Security & RLS     │  <-- Injects territory_code IN (...)
   │  (Users & Permission Matrix) │
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  FX Normalization Engine     │  <-- Dynamic monthly average FX join
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  Freshness Sentinel          │  <-- Checks max business date & sync logs
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  DuckDB Warehouse Execution  │  <-- Deterministic, zero-hallucination SQL
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  Verified Trust Footer       │  <-- Metric ID, Owner, Date Basis, SQL
   └──────────────────────────────┘
```

---

## 3. High-Impact Workflows Delivered

### Workflow 1: Governed Analyst (Trust-First Querying)
- Allows sales reps, regional managers, and leadership to toggle between **Sales Ops Gross Sales (M01)** and **Finance Net Sales (M02)**.
- Automatically injects user-scoped territory filters to guarantee zero data leakage.
- Attaches an auditable **Trust Footer** showing metric definition owner, date basis, currency basis, pipeline freshness stamp, and exact compiled SQL.

### Workflow 2: Distributor 360 Pre-Visit Brief ("The Notebook Killer")
- Designed for field territory managers (e.g. Vidarbha, Maharashtra).
- One-page summary generated in seconds before entering a distributor's shop.
- Highlights:
  - FY26 Sell-In vs. Dealer Scan Sell-Through rate
  - Receivables aging (90+ day overdue and disputed amounts)
  - All pending scheme credit notes with days accrued, putting an end to "we will check" delays.

### Workflow 3: Channel-Risk Radar Sentinel
- Scans distributor sell-in volumes against dealer loyalty scans.
- Flags high-risk inventory loading before products are trucked back as costly returns.
- Backtested on Brazil South: identifies over-stuffed distributors 90 days before the November planting window closes.

---

## 4. Run Steps & Installation

### Prerequisites:
- Python 3.10+
- DuckDB, Streamlit, Pandas, PyYAML

```bash
# Clone the repository
git clone https://github.com/rr-riklr/<repo-name>.git
cd Riklr

# Install dependencies
pip install duckdb streamlit pandas pyyaml

# Run the test suite & gold evaluation benchmark
python -m src.evals.benchmark

# Launch the interactive Streamlit Web App
streamlit run src/ui/app.py
```
