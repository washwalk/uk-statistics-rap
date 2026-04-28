# Adapt This Pattern For Your Statistic

This guide describes how to turn the template or one of the examples into a RAP for another official-statistics output.

## 1. Define The Statistical Product

Write down:

- the user need the output serves
- the headline measure and units
- the expected geography, time period, and population coverage
- the publication frequency
- whether the output is exploratory, management information, official statistics, or accredited official statistics

This prevents the pipeline from becoming a technical exercise without a clear statistical purpose.

## 2. Select And Record Sources

Prefer stable public APIs, metadata endpoints, or reproducible downloads. Record:

- source owner and publication title
- source URL or API endpoint
- dataset ID, edition, version, or release date where available
- licence and attribution requirements
- known source limitations and revision policy

Put stable identifiers in configuration rather than hiding them inside code.

## 3. Define The Expected Grain

State what one row means in each key dataset. Typical grains are:

- one row per period and geography
- one row per period, geography, and measure
- one row per publication date and series identifier

Use the expected grain in validation so duplicate or missing records fail early.

## 4. Build The Pipeline In Stages

Use small stages with clear inputs and outputs:

- `fetch`: retrieve source data and source metadata
- `transform`: create tidy analysis-ready data
- `validate`: check outputs before publication
- `publish`: render reports, dashboards, charts, or tables

Avoid manual edits between these stages. If an adjustment is needed, code it and document why.

## 5. Add Validation For Statistical Risks

Start with generic checks:

- files exist and are non-empty
- required columns are present
- values have expected types and units
- dates parse and sort correctly
- expected grain is unique
- joins do not unexpectedly drop or duplicate records

Then add domain checks:

- valid geography codes
- plausible ranges for rates, indices, or counts
- latest period is not stale
- revisions or movements are within expected bounds, or are flagged for review

## 6. Test Calculations That Could Change The Story

Unit tests should focus on logic that could produce a wrong published message:

- headline period selection
- rate, index, percentage-point, or annual-change calculations
- source filters
- joins and aggregation
- missing value handling

Do not try to unit test every line. Test the statistical decisions and transformations that matter.

## 7. Record Run Metadata

Write `run-metadata.json` on each run. At minimum include:

- project name
- run timestamp
- source URLs
- input and output row counts
- output paths
- validation status

Use the schema in [`run-metadata-schema.md`](run-metadata-schema.md) as the starting point.

## 8. Decide The Publication Control Point

Automation can rebuild an output, but publication may still need human sign-off. Decide:

- when pull requests run offline checks
- when live source checks run
- whether publication is manual, scheduled, or release-based
- who signs off statistical quality, code changes, accessibility, and release timing

## 9. Document Limitations Close To The Output

Users should not need to read code to understand important caveats. Include:

- source limitations
- coverage gaps
- methodology choices
- revision risks
- whether figures are rounded, provisional, or seasonally adjusted

## 10. Review Against The Readiness Matrix

Before moving beyond a prototype, review the pipeline against [`production-readiness-matrix.md`](production-readiness-matrix.md). Record what is demonstrated, what is partial, and what is out of scope for your use case.
