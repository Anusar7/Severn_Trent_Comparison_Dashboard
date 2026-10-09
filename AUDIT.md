# Source and application review — 7 October 2026

## Scope

This is an independent, historical AMP7 review. It retains the October 2025
Ofwat comparison and original 2024/25 company APR history. It does not claim
to incorporate later regulatory revisions or to be a complete compliance audit.

The official web endpoints returned access errors during this rebuild. The
cross-check therefore used the original official PDFs retained with the project,
not newly downloaded editions. Their SHA-256 hashes are in `audit/source-sha256.txt`.
The source register gives the original URLs.

## Data checked

The independent PDF-extraction script performed **335 numeric comparisons**:

| Category | Checks |
|---|---:|
| Company/region peer observations | 183 |
| Latest Severn Trent actuals | 12 |
| Published sector benchmarks | 12 |
| Payment deadbands | 2 |
| Latest full numeric targets | 11 |
| APR historical actuals | 60 |
| Historical numeric targets | 55 |
| **Total** | **335** |

Result: **334 exact matches at the published precision and one documented
source difference**, with no unexplained mismatches. Several comparisons
check the same underlying value in different tables; 335 is a check count,
not a count of unique observations.

The differing value is C-MeX 2024/25: APR 74.42 versus Ofwat 74.43. The app
uses 74.43 and independently matches that value to Ofwat. Every row of the
audit, including the exception, is recorded in `audit/source-checks.csv`.

The 55 historical targets cover 11 measures over five years. C-MeX has no
fixed numeric target. Historical median values from earlier web tables were
removed from this version because those pages could not be freshly rechecked.
Its five-year actuals remain, with the verified 2024/25 median shown as a
separate final-year marker. No five-year C-MeX achievement score is presented.

Ofwat's p9 colour-coded Severn Trent classification was also reviewed visually:
C-MeX, PCC, CRI, internal flooding and pollution are below its assessment level.
This is distinct from the app's full-numeric-target calculation, which includes
treatment compliance and excludes C-MeX. Both counts happen to be five.

## Material interpretation decisions

- **Internal flooding:** Ofwat 1.52 misses 1.34; original APR 1.33 meets it.
  The app shows the original history, a separate Ofwat marker and a prominent
  source warning. No harmonised achievement score or change rate is shown.
  The original APR annual statuses in the overview matrix are explicitly labelled.
- **CRI:** full target 0, payment deadband 2. The APR supports 1.53 for calendar
  2020. We do not import the 3.94 baseline from the conflicting Ofwat table heading.
  Percentage gaps against zero are not calculated.
- **Treatment compliance:** full target 100%, deadband 99%. Numeric comparisons
  govern target achievement, not the APR's inconsistent “Yes” flag at 99.33%.
- **PCC:** peer data use unadjusted three-year-average litres/person/day;
  history uses percentage reduction from baseline. The COVID-adjusted 130.4
  figure is mentioned separately, and still exceeds 129.0. Percentage targets
  come from the revised 2023 APR, not old volume baselines.
- **Leakage:** signs are reversed from Ofwat's signed change so positive means
  reduction. Historical targets are the unchanged percentage commitments in APR2023.
  Comparison is improvement from each company's baseline, not absolute efficiency.
- **Interruptions:** CSV values and chart axes are seconds; metric cards use
  minutes/seconds. The 2023 reporting-method change reduced the result by 24 seconds,
  so not all improvement can be attributed to operational changes.
- **PSR:** scores cover reach only, not all three components of the commitment.
  Lower register reach does not independently prove inadequate customer support.
- **Calendar periods:** CRI, pollution and treatment use calendar 2020–2024,
  mapped to financial reporting years 2020/21–2024/25.
- **Sewer collapses:** 6.31 versus the 6.29 average is a very small comparative gap.
- **Peer ranks:** separately reported operating regions remain separate; ties
  use competition ranks. Published sector benchmarks are not recomputed as
  simple arithmetic means of company rates.

## Application checks

`test_project.py` checks source-audit results and data hashes, record keys,
denominators, zero/equal targets, higher/lower directions, peer ties, calendar
periods, mixed PCC units, source differences and chart/data parity.

Streamlit's AppTest exercises all 16 overview filter combinations, all 12
measure selections, the charts generated for both tabs, and recommendations.
It is an execution and interaction check, not a screenshot or real-browser
layout test. The logo crop was visually checked against the APR cover.

## Verification limits

- No live-browser visual test or Windows desktop test was performed here.
- Rounded published values can affect close comparisons.
- Underlying company submissions were not independently audited; matching a
  publication does not establish that the underlying measurement was correct.
- The flooding source conflict remains unresolved; the app does not conceal it.
- The application is ready to run locally; it has not been deployed to a public host.

