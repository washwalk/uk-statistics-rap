# UK Population Change Explorer

Compact reproducible analytical pipeline using ONS UK population estimates to produce validated area-period data and a static statistical summary.

Published report: `https://washwalk.github.io/uk-statistics-rap/uk-population-change-explorer/`

## Purpose

This project demonstrates a geography-style RAP pattern for official statistics: fetch a source time series, preserve the raw response, standardise observations into area-period data, derive absolute and percentage change, validate outputs, record run metadata, and publish a concise static report.

The example focuses on a single UK-level population series so the pipeline remains small enough to inspect quickly.

## What It Tracks

- Latest UK population estimate.
- Absolute population change from the previous annual observation.
- Percentage population change from the previous annual observation.
- Recent annual observations for the United Kingdom.

## Workflow

```text
ONS time series JSON -> raw cache -> area-period CSV -> validation -> static HTML report
```

Offline tests use committed processed data and fixtures. Live-source refreshes are isolated in `make integration-test` so routine assurance does not depend on network availability.

## Source

- Source: ONS UK population estimate time series, `UKPOP` from dataset `POP`.
- Endpoint: `https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/timeseries/ukpop/pop/data`.
- Licence: Open Government Licence unless otherwise stated by ONS.

## Local Development

```bash
make fetch             # fetch live ONS JSON into data/raw/
make transform         # build the processed area-period CSV and metadata
make validate          # validate existing generated outputs only
make test              # offline unit tests and validation only
make integration-test  # refresh live ONS data, transform, and validate
make report            # refresh live data and build the static report
make clean             # remove generated raw/processed/report outputs
```

## Outputs

- Raw source response: `data/raw/source.json`
- Source fetch metadata: `data/raw/source-metadata.json`
- Processed area-period data: `data/processed/analysis.csv`
- Run metadata: `data/processed/run-metadata.json`
- Static report: `docs/index.html`

## Validation

`src/validate.py` checks that the processed data and run metadata exist, required area-period columns are present, rows are unique by area and period, source series identifiers match the configured series, annual periods are valid and sorted, population counts and changes are numeric, population counts are positive, and metadata row counts and output paths agree with the generated files.

## Assurance Evidence

- Offline evidence: `make test` checks population-change logic and validates the committed processed sample and run metadata without calling the ONS API.
- Live-source evidence: `make integration-test` fetches the configured ONS population time series, derives previous-period change, and validates the result.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Reviewer evidence: `methodology.md`, the README, and the static report explain the source, transformation, validation checks, and limitations.
- Manual controls still needed for production: geography-policy review, statistical sign-off, accessibility review, and revisions handling.

## Interpretation

The change metrics compare each annual UK population estimate with the previous annual observation. They are descriptive indicators and do not explain the demographic drivers of change.

## Limitations

This example demonstrates geography-style validation and derived change calculations. It uses one UK-level series and does not replace detailed population-estimates publications.

## Adapting This Example

To reuse the pattern for another population or geography series, update `config.json` with the source URL, series ID, and measure label, then adjust the area fields and test fixture in `tests/test_transform.py`.
