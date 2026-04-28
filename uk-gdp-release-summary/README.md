# UK GDP Release Summary

Compact reproducible analytical pipeline using ONS GDP index data to produce a validated release-summary dataset and static statistical report.

Published report: `https://washwalk.github.io/uk-statistics-rap/uk-gdp-release-summary/`

## Purpose

This project demonstrates a release-summary RAP pattern for a headline quarterly economic time series. It fetches source data, caches the raw response, derives previous-period growth, validates outputs, records run metadata, and publishes a concise static report.

The example is intentionally narrow: it summarises one GDP chained volume measure index rather than recreating a full national accounts bulletin.

## What It Tracks

- Latest GDP chained volume measure index.
- Previous-quarter growth calculated from the index.
- Recent quarterly observations from the configured ONS series.

## Workflow

```text
ONS time series JSON -> raw cache -> tidy CSV -> validation -> static HTML report
```

Offline tests use committed processed data and fixtures. Live-source refreshes are isolated in `make integration-test` so routine assurance does not depend on network availability.

## Source

- Source: ONS gross domestic product chained volume measure index, `ABMI` from dataset `PN2`.
- Endpoint: `https://www.ons.gov.uk/economy/grossdomesticproductgdp/timeseries/abmi/pn2/data`.
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

`src/validate.py` checks that the processed data and run metadata exist, required columns are present, rows are unique by period and measure, source series identifiers match the configured series, quarterly periods are valid and sorted, values and growth rates are numeric, and metadata row counts and output paths agree with the generated files.

## Assurance Evidence

- Offline evidence: `make test` checks previous-period growth logic and validates the committed processed sample and run metadata without calling the ONS API.
- Live-source evidence: `make integration-test` fetches the configured ONS GDP time series, derives previous-period growth rates, and validates the result.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Reviewer evidence: `methodology.md`, the README, and the static report explain the source, transformation, validation checks, and limitations.
- Manual controls still needed for production: statistical sign-off, release-timing checks, accessibility review, and revisions handling.

## Interpretation

The growth metric is the percentage change in the GDP index from the previous quarterly observation. It is a simple descriptive summary and does not replace the wider ONS national accounts commentary.

## Limitations

This example demonstrates a repeatable release-summary pattern. It uses one GDP series and does not reproduce the full national accounts release.

## Adapting This Example

To reuse the pattern for another ONS index series, update `config.json` with the series URL, series ID, and measure label, then adjust the test fixture in `tests/test_transform.py` to cover the statistic-specific growth calculation.
