# UK Inflation Monitor

Compact RAP example for turning an ONS inflation time series into validated analytical data and a small static report.

## Source

- Source: ONS CPIH annual inflation rate time series, `L55O` from dataset `MM23`.
- Endpoint: `https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l55o/mm23/data`.
- Licence: Open Government Licence unless otherwise stated by ONS.

## Commands

```bash
make validate          # validate existing generated outputs only
make test              # offline unit tests and validation only
make integration-test  # refresh live ONS data, transform, and validate
make report            # refresh live data and build the static report
```

## Assurance Evidence

- Offline evidence: `make test` checks previous-period change logic and validates the committed processed sample and run metadata without calling the ONS API.
- Live-source evidence: `make integration-test` fetches the configured ONS time series and rebuilds `data/processed/analysis.csv`.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Manual controls still needed for production: statistical sign-off, accessibility review, release approval, and source-revisions handling.

## Limitations

This example demonstrates the pipeline pattern, not a complete inflation bulletin. It uses one time series and does not replace ONS inflation releases.

## Adapting This Example

To reuse the pattern for another ONS time series, update `config.json` with the series URL, series ID, and measure label, then adjust the test fixture in `tests/test_transform.py` to cover the statistic-specific calculation.
