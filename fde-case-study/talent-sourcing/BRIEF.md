# talent-sourcing: brief

## The client

A Middle East talent consultancy headquartered in Dubai recruits for 24 corporate clients across six sectors in the Gulf. It also runs offices in Riyadh and Doha. Its 35 recruiters and sourcers handle about 600 roles a year. Client contracts promise a shortlist within 7 to 10 working days from the day a role opens. Clients say the shortlist takes about three weeks to arrive and some of them have started to send roles to other firms.

## The ask

The Managing Partner wants to cut the time from an open role to a shortlist the client accepts. The firm also wants clients to accept more of the shortlists it sends.

Recruiters say they drown in applications. The Managing Partner's starting idea is to use AI to screen CVs faster. You are free to agree or disagree.

Your job:

1. Find out where the time goes between a role opening and the client accepting a shortlist
2. Decide which one or two problems are worth solving first
3. Build a working prototype that fixes them
4. Show how much faster or better the process gets, with numbers

## What is in this folder

| Path | Contents |
|---|---|
| `context/org/` | Company profile, teams, clients and systems |
| `context/transcripts/` | Seven stakeholder interviews from a discovery week |
| `context/documents/` | Intake form, client SLA summary, candidate data policy, ATS field spec, screening call notes, data dictionary |
| `context/documents/sample-job-descriptions/` | Three job descriptions as sent to job boards |
| `context/documents/cv-inbox/` | 50 CVs received for five open roles: PDF, Word and phone photos or scans, in English, Arabic or both. `index.md` lists them. |
| `data/` | ATS export as CSV: clients, hiring managers, recruiters, roles, stage events, candidates, applications, shortlist feedback and FX rates |
| `data/ats.sqlite` | Mock ATS with roles, candidates, applications, shortlist feedback and an empty `parsed_cv` table |

## Things to know

- The interviews reflect what people believe. They may not match the data.
- The data is an export from the client's systems. Treat it as you would treat real client data, including personal data.
- The prototype does not need to connect to the firm's applicant tracking system (ATS). `data/ats.sqlite` stands in for it. Explain what a real connection would need.
- The firm works in English and Arabic. So do its candidates.
- Any resemblance to a real company, person or candidate is coincidental.

Read the 1-pager `Riklr-FDE-Case-Study.pdf` at the root of this repo for what to submit and how you are assessed.
