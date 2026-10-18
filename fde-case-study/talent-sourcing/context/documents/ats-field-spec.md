# ATS field spec

What the firm's applicant tracking system (ATS) stores. `data/ats.sqlite` is a copy of the ATS with the same tables and fields.

## How the ATS is meant to work

- One candidate record per person. A person who applies again should be matched to their existing record, not given a new one.
- One application per candidate record per role
- A CV parser reads each incoming CV and writes one row to `parsed_cv`. A recruiter reviews the row before it updates or creates a candidate record.
- The parser should never write straight into `candidates`

## Per candidate (`candidates` table)

| Field | What the firm stores |
|---|---|
| candidate_id | ATS key. Not printed on any CV. |
| full_name | Name in Latin script |
| full_name_arabic | Name in Arabic script, if the CV has one |
| email | Main email |
| source | Channel that first created the record |
| nationality | Nationality as written by the candidate |
| residence_country, city | Where the candidate lives now |
| gender | As stated by the candidate. Used for reporting only. |
| languages | Languages the candidate lists |
| cv_language | en, ar or mixed |
| years_experience | Total years of work |
| current_title, current_sector | Latest job title and sector |
| expected_salary, salary_currency, salary_period | Salary expectation as stated |
| notice_period_days | Notice period |
| visa_status | Citizen, residence visa (transferable or employer sponsored), visit visa or outside GCC |
| consent_flag | Y if the candidate agreed to be considered for future roles. N if not. Blank if never recorded. |
| record_created_date, last_activity_date | Record dates. Last activity drives the 24 month retention rule. |

## Per application (`applications` table)

| Field | What the firm stores |
|---|---|
| application_id | ATS key |
| candidate_id, role_id | Who applied for what |
| applied_date | Date the CV arrived or the record was attached |
| source | Channel for this application |
| stage_reached | Furthest stage reached |
| screen_out_reason | Why the CV was rejected, if it was |
| shortlist_round | Shortlist round the candidate was sent in |

## Parser output (`parsed_cv` table, empty)

| Field | Meaning |
|---|---|
| parsed_cv_id | Row key |
| source_file | File name in `cv-inbox` |
| role_id | Role the CV came in for |
| candidate_id | Matched candidate record. Blank if no match. |
| match_method | How the match was made, for example email, name or manual |
| match_confidence | 0 to 1 |
| full_name_latin, full_name_arabic | Name in each script, as on the CV |
| email, phone | Contact details |
| nationality | Nationality in English, for example "Saudi" |
| residence_city, residence_country | Where the candidate lives |
| current_title, current_employer | Latest job |
| years_experience | Total years of work |
| expected_salary_amount, expected_salary_currency, expected_salary_period | Salary expectation. Currency as a 3 letter code. Period is monthly or annual. |
| notice_period_days | Notice period in days |
| visa_status | Same values as `candidates.visa_status` |
| languages, skills | Semicolon separated |
| cv_language | en, ar or mixed |
| field_confidence_json | Confidence per field, as JSON |
| parser_version, parsed_at | Which parser wrote the row and when |
| reviewed_by, reviewed_at | Recruiter who checked the row and when |

## What the ATS must not store

- Photos
- Religion, marital status or health information
- Date of birth, except where a client role has a legal age requirement
- Data about a candidate who asked to be deleted
