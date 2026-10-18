# Data dictionary

ATS export taken on 30 September 2026. Covers roles opened from 1 September 2025 to 31 August 2026 and every candidate record in the ATS. All CSV files are UTF-8. `ats.sqlite` holds the same data.

## clients.csv

One row per client.

| Column | Meaning |
|---|---|
| client_id | Client key |
| client_description | Short description. Client names are removed. |
| country | UAE, KSA or Qatar |
| city | Head office city |
| sector | Logistics, Hospitality, Banking, Construction, Retail or Tech |
| nationalisation_programme | National hiring programme the client reports against, if any |
| nationalisation_target_pct | Client's stated company-wide target for national staff. Blank if none. |
| sla_working_days | Contracted working days from role confirmed to first shortlist |
| account_since | Year the client signed with the firm |

## hiring_managers.csv

One row per client hiring manager.

| Column | Meaning |
|---|---|
| hiring_manager_id | Hiring manager key. Names are removed. |
| client_id | Client |
| title | Job title |
| preferred_channel | How the hiring manager prefers to be contacted |

## recruiters.csv

One row per recruiter or sourcer.

| Column | Meaning |
|---|---|
| recruiter_id | Recruiter key. Names are removed. |
| office | Dubai, Riyadh or Doha |
| level | Sourcer, Recruiter, Senior Recruiter or Principal Consultant |
| owns_roles | Y if the person owns roles end to end |
| sector_focus | Main sector, as listed in the HR system |
| start_date | Date joined the firm |

## roles.csv

One row per role (requisition). Intake fields are copied from the intake form by the recruiter.

| Column | Meaning |
|---|---|
| role_id | Role key |
| client_id | Client |
| hiring_manager_id | Hiring manager who raised the role |
| recruiter_id | Recruiter who owns the role |
| office | Office that owns the role |
| role_title | Title as typed by the recruiter |
| sector | Client sector |
| seniority | Junior, Mid or Senior |
| country, city | Where the job is |
| opened_date | Date the role was logged in the ATS |
| must_have_skills | Intake field. Free text. |
| years_exp_min | Intake field. Minimum years of experience. |
| salary_band_min, salary_band_max, salary_band_currency | Intake field. Monthly salary band. |
| nationality_requirement | Intake field "Nationality preference". Free text. |
| languages_required | Intake field |
| interview_panel_named | Y if the intake named the client interview panel |
| jd_versions | Number of JD drafts sent to the hiring manager before approval |
| sla_working_days | SLA that applies to this role |
| status | Open, Filled, Offer declined or Cancelled at export date |
| filled_date | Date the offer was accepted |

## role_stage_events.csv

One row per stage change on a role. A role that needs a new shortlist goes through sourcing to client feedback again, with a higher round number.

| Column | Meaning |
|---|---|
| role_id | Role |
| stage | role_opened, intake_held, jd_approved, posted, sourcing_started, screening_started, shortlist_sent, client_feedback, client_interviews, offer_made, offer_accepted |
| round | Shortlist round. Blank for stages before the first round. |
| event_time_local | Date and time in the local time of the office that logged it |
| logged_by | Recruiter ID, or "system" for automatic events |

## candidates.csv

One row per candidate record in the ATS. A person can have more than one record.

| Column | Meaning |
|---|---|
| candidate_id | Record key |
| full_name | Name in Latin script, as parsed or typed |
| full_name_arabic | Name in Arabic script, where the CV had it |
| email | Email on the record |
| source | Channel that created the record: board_regional, board_saudi, prof_network, referral, internal_db, client_careers_page |
| nationality | Free text |
| residence_country | UAE, KSA, Qatar or Outside GCC |
| city | City of residence |
| gender | M or F, as stated on the CV or application |
| languages | Languages listed on the CV |
| cv_language | en, ar or mixed |
| years_experience | Total years of work experience |
| current_title | Current job title from the CV |
| current_sector | Sector of current employer |
| expected_salary | Salary expectation as stated |
| salary_currency | Currency of expected_salary |
| salary_period | monthly or annual, as stated |
| notice_period_days | Notice period in days |
| visa_status | Citizen, residence visa (transferable or employer sponsored), visit visa or outside GCC |
| consent_flag | Y if the candidate agreed to be considered for future roles, N if not. Blank if not recorded. |
| record_created_date | Date the record was created |
| last_activity_date | Date of the candidate's last activity in the ATS |

## applications.csv

One row per candidate record attached to a role.

| Column | Meaning |
|---|---|
| application_id | Application key |
| candidate_id | Candidate record |
| role_id | Role |
| applied_date | Date the record was attached to the role |
| source | Channel for this application. internal_db means a recruiter or sourcer attached an existing record. |
| stage_reached | Furthest stage: new, cv_rejected, phone_screen, assessed, withdrawn, shortlisted, client_interview, offer_declined, hired |
| screen_out_reason | Reason the CV was rejected, if it was |
| shortlist_round | Round in which the candidate was sent to the client |

## shortlist_feedback.csv

One row per shortlist sent to a client.

| Column | Meaning |
|---|---|
| shortlist_id | Shortlist key |
| role_id | Role |
| round | Shortlist round |
| sent_date | Date the shortlist email went to the client |
| candidates_sent | Number of candidates in the shortlist |
| feedback_date | Date the client's decision was logged |
| decision | accepted (at least one candidate goes to interview), rejected or awaiting |
| logged_reason | Rejection reason picked from the ATS dropdown |
| client_comment | Client feedback pasted from email. Candidates are referred to by position in the shortlist. |

## fx_rates.csv

| Column | Meaning |
|---|---|
| month | YYYY-MM |
| currency | AED, SAR, QAR, USD, INR or PHP |
| units_per_usd | Units of the currency per US dollar. AED, SAR and QAR are pegged. |

## ats.sqlite

SQLite copy of the ATS. See `ats-field-spec.md` for what each field means to the firm.

| Table | Contents |
|---|---|
| roles | Same rows and columns as `roles.csv` |
| candidates | Same rows and columns as `candidates.csv` |
| applications | Same rows and columns as `applications.csv` |
| shortlist_feedback | Same rows and columns as `shortlist_feedback.csv` |
| parsed_cv | Empty. One row per parsed CV, as set out in `ats-field-spec.md`. |

Blank CSV values are NULL in SQLite. Numbers are stored as numbers.

## context/documents/cv-inbox/

| File | Meaning |
|---|---|
| index.md | Each CV file with the role it came in for, the date received and the channel |
| *.pdf, *.docx, *.jpg | CVs as received. Each belongs to one application in the ATS. The file does not carry the candidate ID. |

## context/documents/screening-call-notes.csv

Notes recruiters typed after phone screens, exported from their personal trackers. A sample of 28 calls from the last 12 months.

| Column | Meaning |
|---|---|
| call_id | Call key |
| application_id | Application in `applications.csv` |
| role_id | Role |
| recruiter_id | Recruiter who made the call |
| call_date | Date of the call |
| duration_min | Length of the call in minutes |
| outcome | proceed, reject, no_show or candidate_withdrew |
| notes | Free text in recruiter shorthand. "pm" is per month, "pa" is per year and "d" is days. |
