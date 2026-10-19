# 4-Minute Narrated Video Script: Riklr AI FDE Case Study
**Candidate ID:** `iitmcs_24091540`  
**Target Duration:** 3 minutes 50 seconds  
**Tone:** Authoritative, empathetic, grounded in code and warehouse data.

---

### [00:00 - 00:45] Act 1: The Diagnosis & Why the Chatbot Died
*(Visual: Screen showing Riklr architecture diagram and warehouse query comparisons)*

**Speaker:**
"Hi, I’m candidate `iitmcs_24091540`. When the Chief Digital Officer asked for an always-on AI sales analyst across team chat, review meetings, and field voice apps, the instinctive reaction might be to connect an LLM to the warehouse with Text-to-SQL. 

Last year, the company tried that exact approach—and it collapsed from 85 weekly users down to 8. 

Our audit of the warehouse revealed why: it wasn't because the model wasn't smart; it was because the warehouse had dirty keys, colliding metric definitions, and zero currency guardrails. When users asked for 'total sales', the old bot summed local currencies directly across BRL, EUR, INR, and CAD. That produced an $18 Billion hallucination against an actual net sales figure of around $575 Million. 

Meanwhile, field reps in Vidarbha, India, and Rio Grande do Sul, Brazil, abandoned the tool because language success rates dropped below 18% in Marathi and Portuguese, and over 350 out-of-territory records leaked into the chat.

Today, I’m presenting our production solution: a Governed Metric Engine that replaces prompt-based querying with verified contracts, physical Row-Level Security, and two field-first workflows."

---

### [00:45 - 01:45] Act 2: The Governed Engine & Trust Footer
*(Visual: Open Streamlit UI at localhost:8501, Tab 1 Governed AI Analyst)*

**Speaker:**
"Here is the system running live on the client's DuckDB warehouse. 

In Tab 1, we have the Governed Sales Analyst. Notice the security persona in the sidebar. When I query as the Global Finance Controller, the engine computes Net Sales under the Finance definition—M02. It joins monthly average FX rates dynamically, cleans up legacy territory codes, and returns exactly $575.2 Million USD.

Look at the Trust Footer below every single answer. It explicitly states the Metric ID, the owning team, the date and currency basis, the pipeline freshness stamp, and the exact compiled SQL. 

Now, let's test security. I switch my persona to the Territory Manager for Vidarbha, India (`IN-W01`), and attempt to query Brazil South (`BR-S01`). 

Instead of letting an LLM hallucinate or leak sensitive distributor data, the security engine injects Row-Level Security directly into the SQL AST. The query is rejected with a clean `ACCESS_DENIED` notice. Zero data leakage."

---

### [01:45 - 02:45] Act 3: Distributor 360 Pre-Visit Brief
*(Visual: Switch to Tab 2 in Streamlit, select Ramonis Agri Traders in Vidarbha, toggle Marathi/English)*

**Speaker:**
"Now let's look at the field reality. In his interview, the Vidarbha territory manager showed us his paper notebook. Every Monday, he visits distributors who refuse to pay invoices because their scheme credits haven't been issued for six months. Finance tells him 'we will check', leaving him stuck in the middle.

Tab 2 is our Distributor 360 Pre-Visit Brief—what the territory manager called 'the notebook killer'. 

In three seconds, before stepping out of his vehicle, he opens his mobile screen. He selects the distributor. The engine aggregates FY26 sell-in, end-grower scan sell-through rate, overdue receivables, and—crucially—all pending scheme credit notes with their exact aging. 

Now, instead of a ten-minute argument about unissued rebates, he walks in with verified numbers in hand, available in English, Marathi, or Hindi."

---

### [02:45 - 03:20] Act 4: Channel-Risk Radar Sentinel
*(Visual: Switch to Tab 3, select Region BR, click Run Risk Scan)*

**Speaker:**
"Finally, let's examine the $8.0 Million return crisis in Southern Brazil. Leadership believed this was caused by an unpredictable drought in November. 

Our data audit proved otherwise: dealer scans had already collapsed to 0.19 by September, yet distributors were loaded with 2 to 3 times normal volume so sales reps could hit their quarterly incentive caps.

Tab 3 is our Channel-Risk Radar Sentinel. It cross-references distributor sell-in against dealer loyalty scans. 

Running it on Brazil immediately flags 11 distributors where sell-in outpaced scan sell-through by more than 2.5 times. This provides regional sales leadership with a 90-day early warning before products are trucked back as returns, protecting millions in working capital."

---

### [03:20 - 03:50] Act 5: Impact & Conclusion
*(Visual: Show Gold Evaluation benchmark passing in terminal `python -m src.evals.benchmark`)*

**Speaker:**
"We verified our solution with a comprehensive Gold Benchmark test covering currency traps, RLS leakage, pipeline freshness, and stuck credits. The governed engine achieves a 100% pass rate.

By shifting from an ungrounded chatbot to a governed metric engine with field decision workflows, we eliminate days of BI backlog, protect millions in inventory return risk, and give the sales team tools they can trust in the field.

All code, unit tests, notebooks, and deck slides are committed to the repository. Thank you."
