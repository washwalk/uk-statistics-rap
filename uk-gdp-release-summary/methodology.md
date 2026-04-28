# Methodology

## Purpose

The UK GDP Release Summary provides a concise view of a headline GDP index using a reproducible release-summary workflow.

## Source Data

The pipeline uses the public ONS time series JSON endpoint for series `ABMI` in dataset `PN2`. ONS content is available under the Open Government Licence unless otherwise stated by ONS.

## Processing

The pipeline performs five steps:

1. Fetch the configured ONS JSON response and store it in `data/raw/source.json`.
2. Extract quarterly observations with non-blank numeric values.
3. Convert observations into a tidy CSV with period, period type, measure, index value, previous-period growth, and source series.
4. Record source URL, input row counts, output row counts, output paths, and validation status in `data/processed/run-metadata.json`.
5. Build `docs/index.html` from the validated processed data.

## Calculation

Previous-period growth is calculated as `(current index / previous index - 1) * 100`. The result is reported as a percentage. Growth is left blank where no previous value exists or the previous value is zero.

## Validation Rules

Validation checks include:

- Processed data and run metadata exist.
- Required columns are present.
- Period and measure rows are unique.
- Quarterly periods are valid and sorted.
- Index values and growth rates are numeric where populated.
- Source series and source URL match `config.json`.
- Metadata row counts and output paths match the generated outputs.

## Limitations

- The summary uses one GDP index series only.
- It does not reproduce the full national accounts release.
- ONS GDP estimates can be revised.
- Short-term quarterly movement should be read alongside wider national accounts commentary.

## Future Extensions

- Add expenditure, income, or output breakdowns.
- Add revision tracking between releases.
- Add chart output while retaining an offline test path.
