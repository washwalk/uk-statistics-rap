# UK GDP Release Summary

Compact RAP example for turning an ONS GDP index time series into a validated release-summary dataset and static report.

## Source

- Source: ONS gross domestic product chained volume measure index, `ABMI` from dataset `PN2`.
- Endpoint: `https://www.ons.gov.uk/economy/grossdomesticproductgdp/timeseries/abmi/pn2/data`.
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
- Live-source evidence: `make integration-test` fetches the configured ONS GDP time series, derives previous-period growth rates, and validates the result.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, outputs, and validation status.
- Manual controls still needed for production: statistical sign-off, release-timing checks, accessibility review, and revisions handling.

## Limitations

This example demonstrates a repeatable release-summary pattern. It uses one GDP series and does not reproduce the full national accounts release.
