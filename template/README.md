# GSS RAP Starter Template

Use this folder as a minimal starting point for a reproducible analytical pipeline using official statistics. Copy the folder, rename it for your output, and replace the placeholder source, schema, validation, and publication logic with project-specific code.

## What To Replace

- `config.yml`: source URL, expected grain, required columns, and output paths.
- `src/fetch.py`: source download and raw metadata capture.
- `src/transform.py`: deterministic transformation from raw data to analysis-ready data.
- `src/validate.py`: checks for files, schema, duplicates, missingness, plausible values, and run metadata.
- `src/publish.py`: report, dashboard, or publication output generation.
- `tests/`: unit tests for calculations and transformation logic that could change the published statistic.

## Standard Commands

```bash
make install
make fetch
make transform
make validate
make test
make integration-test
make report
make clean
```

`make test` should stay offline. It should validate existing outputs and run local unit tests without calling source APIs. Use `make integration-test` when you need to refresh live source data.

## Expected Outputs

- `data/raw/source.csv`: downloaded source data or equivalent raw extract.
- `data/raw/source-metadata.json`: source URL, retrieval timestamp, and source metadata.
- `data/processed/analysis.csv`: tidy analysis-ready dataset.
- `data/processed/run-metadata.json`: machine-readable audit metadata for the pipeline run.
- `outputs/`: generated tables, figures, or rendered publication assets.

## Production Notes

Before using this template for a live official-statistics output, add the controls appropriate to the publication risk: peer review, accessibility checks, disclosure control, dependency management, release sign-off, and incident handling.
