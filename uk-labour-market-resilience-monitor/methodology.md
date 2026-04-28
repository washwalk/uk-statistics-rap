# Methodology

## Purpose

The UK Labour Market Resilience Monitor provides a concise view of headline UK labour market signals using reproducible data collection, validation, and static reporting.

## Source Data

The monitor uses public ONS time series JSON endpoints from `www.ons.gov.uk`. Current indicators are employment rate, unemployment rate, economic inactivity rate, vacancies, and regular pay growth.

## Processing

The pipeline performs four steps:

1. Fetch raw ONS JSON responses and cache them in `data/raw/`.
2. Extract monthly, quarterly, or annual observations depending on the source series.
3. Convert values into tidy rows with indicator metadata, source URLs, periods, values, and units.
4. Build dashboard-ready JSON in `docs/data/indicators.json` and a static HTML dashboard in `docs/index.html`.

## Validation Rules

Validation checks include:

- Raw files exist for each configured indicator.
- Source payloads contain recognised observations.
- Processed data are not empty.
- Required columns are present.
- Values are numeric.
- Percentage indicators are not negative.
- Latest snapshot and dashboard data are generated.

## Resilience Signals

Each card compares the latest observation with the previous observation. Direction is interpreted as follows:

- Employment rate and regular pay growth: higher is treated as improving.
- Unemployment rate and economic inactivity rate: lower is treated as improving.
- Vacancies are treated as contextual because higher vacancies can signal demand but also recruitment difficulty.

## Limitations

- The dashboard is descriptive and should not be interpreted as causal analysis.
- ONS time series may be revised.
- Latest-period changes can be noisy.
- National-level indicators can mask regional, demographic, or sectoral differences.
- The first version does not include confidence intervals or uncertainty estimates.

## Future Extensions

- Add regional labour market indicators.
- Add Census 2021 context on economic activity by age, sex, disability, unpaid care, and health.
- Add revisions tracking between automated runs.
- Add a more formal composite resilience index if the weighting method is clearly justified.
