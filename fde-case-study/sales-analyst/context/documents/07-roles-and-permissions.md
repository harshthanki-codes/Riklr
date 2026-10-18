# Roles and data permissions

- **Owner:** Data and BI team with Finance
- **Version:** June 2024
- **Full matrix:** `data/permission_matrix.csv`

## Rules

- Each user has one role in `users_and_roles`
- Scope comes from the user's territory, sub-region or region
- A role with no row for a data domain has no access to it
- `*` means all domains unless a more specific row says otherwise

## Summary by role

| Role | Sees | Does not see |
|---|---|---|
| Chief Digital Officer | Global aggregates | Distributor receivables |
| Global Sales Head | Everything | |
| Global Finance Controller | Everything | |
| Regional Sales Manager | All commercial domains in own sub-region | Other sub-regions |
| Regional Finance Controller | Everything in own region | Other regions |
| Territory Manager | All commercial domains in own territory | Other territories |
| Key Account Manager | Assigned distributors only (`distributors.kam_user_id`) | Targets. Other distributors. |
| Field Agronomist | Own territory: scans and sell-in quantities. Weather. | Amounts and receivables. Credits and targets. |
| Sales Operations Analyst | Own region, all domains except receivables | Receivables |
| Loyalty Program Manager | Own region: scans and loyalty schemes. Sell-in quantities. | Amounts, receivables |
| BI Analyst | Everything, for maintenance | Should not use access for business questions |

## Sub-regions

| Sub-region | Territories |
|---|---|
| NA | All NA territories |
| BR-South | BR-S01 to BR-S04 |
| BR-Center | BR-C01 to BR-C04 |
| EU | All EU territories |
| IN-North-Central | IN-N01 to IN-N03, IN-C01 |
| IN-West-South | IN-W01 to IN-W03, IN-S01 to IN-S03 |

## Known gaps

- Dashboards apply these rules through row filters in the BI tool
- The 2025 sales bot used one service account and did not apply them
