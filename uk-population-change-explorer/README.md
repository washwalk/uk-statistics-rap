# UK Population Change Explorer

Compact RAP example for turning an ONS population time series into validated area-period data and a small static report.

## Source

- Source: ONS UK population estimate time series, `UKPOP` from dataset `POP`.
- Endpoint: `https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/timeseries/ukpop/pop/data`.
- Licence: Open Government Licence unless otherwise stated by ONS.

## Commands

```bash
make validate          # validate existing generated outputs only
make test              # offline validation only
make integration-test  # refresh live ONS data, transform, and validate
make report            # refresh live data and build the static report
```

## Assurance Evidence

- Offline evidence: `make test` validates the committed processed sample and run metadata without calling the ONS API.
- Live-source evidence: `make integration-test` fetches the configured ONS population time series, derives previous-period change, and validates the result.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Manual controls still needed for production: geography-policy review, statistical sign-off, accessibility review, and revisions handling.

## Limitations

This example demonstrates geography-style validation and derived change calculations. It uses one UK-level series and does not replace detailed population-estimates publications.
