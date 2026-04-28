# Methodology

## Purpose

The UK Population Change Explorer provides a concise view of UK population change using a reproducible area-period data workflow.

## Source Data

The pipeline uses the public ONS time series JSON endpoint for series `UKPOP` in dataset `POP`. ONS content is available under the Open Government Licence unless otherwise stated by ONS.

## Processing

The pipeline performs five steps:

1. Fetch the configured ONS JSON response and store it in `data/raw/source.json`.
2. Extract annual observations with non-blank numeric values.
3. Convert observations into an area-period CSV with UK geography fields, population count, absolute change, percentage change, and source series.
4. Record source URL, input row counts, output row counts, output paths, and validation status in `data/processed/run-metadata.json`.
5. Build `docs/index.html` from the validated processed data.

## Calculation

Absolute change is calculated as the current annual population estimate minus the previous annual estimate. Percentage change is calculated as `(current population / previous population - 1) * 100`.

## Validation Rules

Validation checks include:

- Processed data and run metadata exist.
- Required area-period columns are present.
- Area-period rows are unique.
- Annual periods are valid and sorted.
- Population counts are positive integers.
- Absolute and percentage changes are numeric where populated.
- Source series and source URL match `config.json`.
- Metadata row counts and output paths match the generated outputs.

## Limitations

- The explorer uses one UK-level series only.
- It does not include subnational geographies, components of change, or uncertainty.
- Population estimates can be revised as methods and inputs improve.
- The output is descriptive and does not explain demographic drivers.

## Future Extensions

- Add country, region, or local authority series where comparable sources are available.
- Add births, deaths, and migration components.
- Add revisions tracking between runs.
