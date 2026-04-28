# UK Inflation Monitor

Compact reproducible analytical pipeline using ONS CPIH data to produce a validated inflation monitoring dataset and static statistical summary.

Published report: `https://washwalk.github.io/uk-statistics-rap/uk-inflation-monitor/`

## Purpose

This project demonstrates how a small official-statistics time series can be handled through a production-style RAP workflow: fetch source data, preserve a raw response, transform observations into tidy analytical data, validate outputs, record run metadata, and publish a short static report.

The monitor focuses on the headline CPIH annual inflation rate. It is deliberately scoped as a concise example rather than a full inflation bulletin.

## What It Tracks

- Latest CPIH annual inflation rate.
- Previous-period absolute change in percentage points.
- Recent monthly observations from the configured ONS time series.

## Workflow

```text
ONS time series JSON -> raw cache -> tidy CSV -> validation -> static HTML report
```

The pipeline is designed so that an offline test run can validate the committed sample outputs, while a separate integration run can refresh from the live ONS endpoint.

## Source

- Source: ONS CPIH annual inflation rate time series, `L55O` from dataset `MM23`.
- Endpoint: `https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l55o/mm23/data`.
- Licence: Open Government Licence unless otherwise stated by ONS.

## Local Development

```bash
make fetch             # fetch live ONS JSON into data/raw/
make transform         # build the processed analytical CSV and metadata
make validate          # validate existing generated outputs only
make test              # offline unit tests and validation only
make integration-test  # refresh live ONS data, transform, and validate
make report            # refresh live data and build the static report
make clean             # remove generated raw/processed/report outputs
```

## Outputs

- Raw source response: `data/raw/source.json`
- Source fetch metadata: `data/raw/source-metadata.json`
- Processed analytical data: `data/processed/analysis.csv`
- Run metadata: `data/processed/run-metadata.json`
- Static report: `docs/index.html`

## Validation

`src/validate.py` checks that the processed data and run metadata exist, required columns are present, rows are unique by period and measure, source series identifiers match the configured series, monthly periods are valid and sorted, values and changes are numeric, and metadata row counts and output paths agree with the generated files.

## Assurance Evidence

- Offline evidence: `make test` checks previous-period change logic and validates the committed processed sample and run metadata without calling the ONS API.
- Live-source evidence: `make integration-test` fetches the configured ONS time series and rebuilds `data/processed/analysis.csv`.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Reviewer evidence: `methodology.md`, the README, and the static report explain the source, transformation, validation checks, and limitations.
- Manual controls still needed for production: statistical sign-off, accessibility review, release approval, and source-revisions handling.

## Interpretation

The change metric is the difference between the latest CPIH annual inflation rate and the previous monthly observation. It is a descriptive monitoring indicator, not a forecast or policy assessment.

## Limitations

This example demonstrates the pipeline pattern, not a complete inflation bulletin. It uses one time series and does not replace ONS inflation releases.

## Adapting This Example

To reuse the pattern for another ONS time series, update `config.json` with the series URL, series ID, and measure label, then adjust the test fixture in `tests/test_transform.py` to cover the statistic-specific calculation.
