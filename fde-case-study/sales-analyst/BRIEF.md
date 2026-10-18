# sales-analyst: brief

## The client

A global agri-inputs company sells seeds, crop protection products and biologicals. This case covers its commercial business in 4 regions: North America, Brazil, Europe and India. The company sells to about 130 distributors who sell on to about 1,100 dealers. The dealers in turn sell to growers. All sales data sits in a cloud data warehouse. The fiscal year runs from October to September and FY2026 has just closed.

## The ask

The Chief Digital Officer wants an always-on AI analyst for the sales team. Anyone in sales should be able to ask a question and get an answer from company data in seconds. The analyst should sit in the team chat tool, join review meetings and work as a voice assistant in the field app. Access must follow the role permissions already in place. If it works, other business units will adopt it.

You are free to agree or disagree with this idea.

Your job:

1. Find out how the sales team plans and decides today, and where that breaks
2. Decide which one or two problems are worth solving first
3. Build a working prototype that solves them on the data provided
4. Show how you would prove it helps, with numbers

## What is in this folder

| Path | Contents |
|---|---|
| `context/org/` | Company profile, regions, teams and systems |
| `context/transcripts/` | Seven stakeholder interviews from a discovery week |
| `context/documents/` | Concept note and Riklr call notes. Metric definitions and permissions. Old bot notes and the data dictionary. |
| `data/` | A warehouse extract as CSV files, plus the same tables in `warehouse.duckdb` |

## Things to know

- The interviews reflect what people believe. They may not match the data
- The data is an extract from the client's warehouse as of 30 September 2026. Treat it as you would treat real client data
- You can open `warehouse.duckdb` with DuckDB from Python, the CLI or most SQL tools. The CSVs hold the same rows
- The prototype does not need to connect to the client's chat tool, field app or warehouse. Mock what you need and say what the real integration would require
- Any resemblance to a real company, person or product is coincidental

Read the 1-pager at the root of this repo (`Riklr-FDE-Case-Study.pdf`) for what to submit and how you are assessed.
