# Methodology

## Purpose

The UK Inflation Monitor provides a concise view of headline CPIH annual inflation using a reproducible data collection, transformation, validation, and publication workflow.

## Source Data

The pipeline uses the public ONS time series JSON endpoint for series `L55O` in dataset `MM23`. ONS content is available under the Open Government Licence unless otherwise stated by ONS.

## Processing

The pipeline performs five steps:

1. Fetch the configured ONS JSON response and store it in `data/raw/source.json`.
2. Extract monthly observations with non-blank numeric values.
3. Convert observations into a tidy CSV with period, period type, measure, value, previous-period change, and source series.
4. Record source URL, input row counts, output row counts, output paths, and validation status in `data/processed/run-metadata.json`.
5. Build `docs/index.html` from the validated processed data.

## Calculation

Previous-period change is calculated as the latest CPIH annual inflation rate minus the previous monthly rate. The result is reported in percentage points.

## Validation Rules

Validation checks include:

- Processed data and run metadata exist.
- Required columns are present.
- Period and measure rows are unique.
- Monthly periods are valid and sorted.
- Values and changes are numeric where populated.
- Source series and source URL match `config.json`.
- Metadata row counts and output paths match the generated outputs.

## Limitations

- The monitor uses one headline CPIH series only.
- It does not reproduce the full ONS inflation statistical bulletin.
- ONS time series can be revised.
- Latest-period movement should be read alongside wider inflation context.

## Future Extensions

- Add CPI, CPIH component, or goods/services comparisons.
- Add revisions tracking between runs.
- Add chart output while retaining an offline test path.
