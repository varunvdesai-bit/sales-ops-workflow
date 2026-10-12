# Data Validation Report -- week of 2026-07-11

**2 issue(s) found (2 need attention before trusting this week's numbers).**

## Summary

- **Duplicates:** OK, nothing found.
- **Missing values:** 1 issue(s) found -- see below.
- **Join problems:** OK, nothing found.
- **Impossible values:** 1 issue(s) found -- see below.

## Missing values

- 'wins.is_duplicate' is blank on 9614 row(s) (100.0% of the table) -- this field should always be filled in.

| win_id   | opp_id   | account_id   | week_ending         | fiscal_quarter   |   fiscal_week | channel   | seller_id   | product   |   units |   arr_booked |   play_id | seller_name   | industry                 | annual_revenue_band   | region   | is_BAU   |   is_duplicate |
|:---------|:---------|:-------------|:--------------------|:-----------------|--------------:|:----------|:------------|:----------|--------:|-------------:|----------:|:--------------|:-------------------------|:----------------------|:---------|:---------|---------------:|
| W50085   | O80085   | A20085       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S159        | Advanced  |       1 |        32041 |       nan | Rhea Okafor   | Nonprofit                | $5M-$10M              | West     | True     |            nan |
| W50086   | O80086   | A20086       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S159        | Advanced  |       1 |        11527 |       nan | Rhea Okafor   | Construction             | $5M-$10M              | East     | True     |            nan |
| W50087   | O80087   | A20087       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S159        | Advanced  |       1 |        19731 |       nan | Rhea Okafor   | Wholesale & Distribution | $2.5M-$5M             | East     | True     |            nan |
| W50088   | O80088   | A20088       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S156        | Advanced  |       1 |        17402 |       nan | Bryn Moreau   | Wholesale & Distribution | $5M-$10M              | East     | True     |            nan |
| W50089   | O80089   | A20089       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S153        | Advanced  |       1 |         9510 |       nan | Uma Moreau    | Professional Services    | $1M-$2.5M             | West     | True     |            nan |
| W50090   | O80090   | A20090       | 2025-02-08 00:00:00 | FY25Q3           |             1 | Hunters   | S155        | Advanced  |       1 |        12158 |       nan | Rhea Ruiz     | Professional Services    | $5M-$10M              | East     | True     |            nan |


## Impossible values

- 1 funnel row(s) show a stage with MORE records than the stage that feeds it (e.g. more SQLs than MQLs) -- that can't happen if each stage is a subset of the one before it.

| fiscal_quarter   |   fiscal_week | channel   |   leads |   mqls |   sqls |   opps_created |
|:-----------------|--------------:|:----------|--------:|-------:|-------:|---------------:|
| FY26Q4           |             7 | Inbound   |      97 |     43 |     46 |             36 |


## Notes

- Ignored 4 blank/unlabeled column(s) in 'plans' -- leftover Excel formatting, not real data.
- Ignored 1 blank/unlabeled column(s) in 'plays' -- leftover Excel formatting, not real data.
