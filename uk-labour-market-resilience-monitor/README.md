# UK Labour Market Resilience Monitor

Automated ONS API dashboard tracking UK labour market resilience through reproducible data pipelines, quality checks, and GitHub Pages reporting.

This project fetches headline labour market time series from the Office for National Statistics, validates the data, creates tidy outputs, and builds a static public dashboard. It is designed as a GSS interview portfolio project showing reproducible analytical pipelines, official statistics handling, automation, QA, and clear public communication.

## What It Tracks

- Employment rate
- Unemployment rate
- Economic inactivity rate
- Vacancies
- Regular pay growth

The first working version focuses on national-level labour market signals. Regional and Census 2021 extensions are documented as future improvements.

## Run Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/fetch_ons.py
.venv/bin/python src/transform.py
.venv/bin/python src/validate.py
.venv/bin/python src/build_site.py
```

Open `docs/index.html` in a browser to view the generated dashboard.

The project also supports the shared repository command contract:

```bash
make fetch
make transform
make validate
make test
make integration-test
make report
make clean
```

Use `make test` for offline validation of existing outputs. Use `make integration-test` to fetch live ONS data, transform it, and validate refreshed outputs. Use `make report` for the full refresh and dashboard rebuild.

## Project Structure

- `src/fetch_ons.py`: fetches source JSON from ONS.
- `src/transform.py`: creates processed CSV/JSON outputs.
- `src/validate.py`: runs data quality checks.
- `src/build_site.py`: generates the static dashboard.
- `data/raw/`: cached raw API responses, ignored by Git.
- `data/processed/`: processed analytical outputs and run metadata.
- `docs/`: GitHub Pages site.
- `.github/workflows/update-and-publish.yml`: scheduled rebuild workflow.
- `Makefile`: standard local commands for fetch, transform, validate, test, report, and clean.

## GitHub Pages

The dashboard is generated into `docs/`. Configure GitHub Pages to serve from the `main` branch and `/docs` folder.

## Data Sources

Data are sourced from public ONS time series pages and JSON endpoints. ONS content is available under the Open Government Licence unless otherwise stated.

## Interpretation

The monitor uses simple latest-period direction indicators. It is not a forecast, causal model, or replacement for ONS labour market bulletins. Labour market statistics can be revised, so each rebuild represents the latest reproducible view from the source data.
