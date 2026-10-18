# Data dictionary

- **Owner:** Data and BI team
- **Extract date:** 30 September 2026
- **Format:** One CSV per table in `data/`. The same tables are in `data/warehouse.duckdb`
- **Fiscal year:** 1 October to 30 September. FY2026 runs from 1 October 2025 to 30 September 2026
- **Coverage:** Transactions from 1 July 2024 unless stated

Tables are loaded as received from source systems. They have not been cleaned.

## Reference tables

### regions

| Column | Description |
|---|---|
| region_code | NA, BR, EU or IN |
| region_name | Region name |
| hemisphere | Northern or Southern |
| currencies | Billing currencies used in the region |
| main_sell_in_months | Main months when distributors buy |

### territories

| Column | Description |
|---|---|
| territory_code | Current territory code, for example `BR-S01` |
| region_code | Region |
| sub_region | Unit managed by one regional sales manager |
| territory_name | Area name |
| country | ISO country code |
| currency | Billing currency for the territory |
| legacy_code | Code used in the CRM before 2023 |
| main_language | Main working language of the field team |

### products

| Column | Description |
|---|---|
| product_id | Product code |
| product_name | Product and pack |
| category | Seeds, Crop Protection or Biologicals |
| sub_category | For example Corn seed or Fungicide |
| crop | Main crop |
| pack_size | Selling unit |
| list_price_usd | Global list price per pack. Local prices differ. |
| regions_sold | Regions where the product is sold |

### distributors

| Column | Description |
|---|---|
| distributor_id | Distributor code |
| distributor_name | Trading name |
| region_code | Region |
| territory_code | Home territory. All of the distributor's business books here. |
| currency | Billing currency |
| tier | Platinum, Gold or Silver |
| onboarded_date | First month of trading |
| credit_limit_local | Credit limit in billing currency |
| kam_user_id | Key account manager, if one is assigned |

### dealers

| Column | Description |
|---|---|
| dealer_id | Dealer code |
| dealer_name | Trading name |
| distributor_id | Main supplying distributor |
| territory_code | Territory |
| country | ISO country code |
| in_loyalty_program | Y if enrolled in the scan program |
| program_joined_date | Enrollment date |

### users_and_roles

| Column | Description |
|---|---|
| user_id | User code |
| role | Job role. Drives permissions. |
| region | Region, blank for global roles |
| sub_region | Sub-region, where relevant |
| territory_code | Territory, for territory managers and agronomists |
| primary_language | Working language (ISO code) |
| country | Base country |
| joined_date | Joined the company |

### permission_matrix

| Column | Description |
|---|---|
| role | Role |
| data_domain | One of: sell_in / returns / targets / dealer_scans / receivables / schemes_credits / weather / `*` |
| access_scope | One of: Global / Own region / Own sub-region / Own territory / Assigned distributors / None |
| notes | Exceptions |

### metric_definitions

| Column | Description |
|---|---|
| metric_id | Metric code |
| metric_name | Name as used by the owning team |
| owner_team | Team that wrote the definition |
| definition | Plain-language definition |
| formula | Formula as written by the owner |
| currency_rule | How currencies are handled |
| date_basis | Date used to assign a period |
| last_reviewed | Last review date |
| used_in | Where the definition is used |

## Transaction tables

### sell_in_orders

One row per invoice line from the company to a distributor.

| Column | Description |
|---|---|
| line_id | Invoice line code |
| order_id | Order code. One order can have several lines. |
| order_date | Date the distributor placed the order |
| invoice_date | Date of the invoice |
| distributor_id | Distributor |
| territory_code | Territory as booked on the transaction |
| product_id | Product |
| doc_type | Document type |
| quantity | Packs |
| unit_price_local | Price per pack before discount |
| discount_pct | On-invoice discount |
| invoice_amount_local | quantity x unit price x (1 - discount) |
| currency | Billing currency |

Brazil rows run to the last successful Brazil load. Other regions run to 29 September 2026.

### returns

One row per return credited to a distributor.

| Column | Description |
|---|---|
| return_id | Return code |
| return_date | Date the goods came back |
| credit_note_date | Date the return credit note was raised |
| distributor_id | Distributor |
| territory_code | Territory as booked |
| product_id | Product |
| original_order_id | Order the goods came from |
| quantity | Packs returned |
| credit_amount_local | Value credited |
| currency | Billing currency |
| reason | Reason code entered by the regional team |

### dealer_scans

Packs scanned by enrolled dealers when sold to a grower. Weekly totals.

| Column | Description |
|---|---|
| week_start | Monday of the scan week |
| dealer_id | Dealer |
| product_id | Product |
| packs_scanned | Packs scanned that week |

Only enrolled dealers scan. Not every enrolled dealer scans every sale.

### schemes_and_credits

One row per scheme credit per distributor per settlement period.

| Column | Description |
|---|---|
| credit_id | Credit code |
| scheme_id | Scheme code |
| scheme_name | Scheme name |
| scheme_type | One of: Volume rebate / Early order / Loyalty / Seasonal push / Price protection |
| distributor_id | Distributor |
| territory_code | Territory |
| currency | Billing currency |
| period_start | Start of the settlement period |
| period_end | End of the settlement period |
| accrual_date | Date finance accrued the credit |
| issue_date | Date the credit note was issued. Blank if not issued. |
| status | Accrued, Issued or Cancelled |
| amount_local | Credit value |

### receivables_aging

One row per distributor per month end, from 31 July 2024 to 31 August 2026.

| Column | Description |
|---|---|
| snapshot_date | Month end |
| distributor_id | Distributor |
| distributor_name | Distributor name at snapshot |
| territory_code | Territory |
| currency | Billing currency |
| credit_limit_local | Credit limit |
| total_outstanding_local | All open invoices |
| not_due_local | Open and not yet due |
| overdue_1_30_local | 1 to 30 days past due |
| overdue_31_60_local | 31 to 60 days past due |
| overdue_61_90_local | 61 to 90 days past due |
| overdue_90_plus_local | Over 90 days past due |
| disputed_local | Overdue amount flagged as disputed against a pending credit |

### targets

Gross sell-in targets on the Sales Operations definition.

| Column | Description |
|---|---|
| territory_code | Territory |
| fiscal_year | FY2025 or FY2026 |
| fiscal_quarter | Q1 (Oct to Dec) to Q4 (Jul to Sep) |
| quarter_start | First day of the quarter |
| product_category | Seeds, Crop Protection or Biologicals |
| currency | Territory currency |
| target_gross_local | Target value |

### weather_weekly

| Column | Description |
|---|---|
| week_start | Monday of the week |
| territory_code | Territory |
| rainfall_mm | Rainfall in the week |
| normal_rainfall_mm | 20-year average for the week |
| rainfall_pct_of_normal | Rainfall as a percentage of normal |
| avg_temp_c | Mean temperature |

### fx_rates

| Column | Description |
|---|---|
| rate_date | Business day |
| currency | One of: CAD / BRL / EUR / GBP / INR |
| local_per_usd | Units of local currency per 1 USD |

USD has no rows. Weekends have no rows.

## Operational tables

### table_load_log

One row per nightly load since 1 July 2026.

| Column | Description |
|---|---|
| load_id | Load code |
| table_name | Target table |
| source_system | Source |
| region | Region loaded, or GLOBAL |
| load_started_at | Start time |
| load_completed_at | End time |
| status | Success, Skipped or Failed with a reason |
| rows_loaded | Rows written |
| max_business_date | Latest business date in the load. Blank if the load did not succeed. |

### old_bot_usage_log

One row per question asked to the 2025 sales bot, from launch to the extract date.

| Column | Description |
|---|---|
| query_id | Question code |
| asked_at | Timestamp |
| user_id | User |
| user_role | Role at the time |
| user_territory | User's territory, if any |
| channel | team_chat or web |
| language_detected | Language of the question |
| question_text | Question as typed |
| status | Answered, Not understood, Error or Timeout |
| response_seconds | Time to respond |
| feedback | up, down or blank |
| feedback_comment | Free text with the feedback |
