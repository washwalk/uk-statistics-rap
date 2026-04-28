# UK Statistics RAP

Examples and guidance for reproducible analytical pipelines (RAP) using UK official statistics.

This repository brings together six small statistical production examples that fetch public Office for National Statistics (ONS) data, process it reproducibly, run quality checks, and publish user-facing outputs through GitHub Pages. It is designed as a practical learning resource for Government Statistical Service (GSS) analysts who want to see how RAP principles can be applied to common statistical outputs.

## Who This Is For

- GSS analysts building or improving statistical production pipelines.
- Statistical teams moving from manual spreadsheets to repeatable code-based workflows.
- Reviewers who need examples of transparent source metadata, documented methodology, and automated publication.
- Interview or portfolio users who want to demonstrate practical official-statistics production skills.

## Live Outputs

- [Labour Market Resilience Monitor](https://washwalk.github.io/uk-statistics-rap/uk-labour-market-resilience-monitor/)
- [ONS Retail Sales RAP](https://washwalk.github.io/uk-statistics-rap/ons-retail-sales-rap/)
- [UK Housing Affordability Monitor](https://washwalk.github.io/uk-statistics-rap/uk-housing-affordability-monitor/)
- [UK Inflation Monitor](https://washwalk.github.io/uk-statistics-rap/uk-inflation-monitor/)
- [UK GDP Release Summary](https://washwalk.github.io/uk-statistics-rap/uk-gdp-release-summary/)
- [UK Population Change Explorer](https://washwalk.github.io/uk-statistics-rap/uk-population-change-explorer/)

## Example Projects

| Project | Topic | Main output | RAP practices shown |
| --- | --- | --- | --- |
| `uk-labour-market-resilience-monitor/` | Labour market indicators | Static HTML dashboard | API fetch, validation, processed data, dashboard generation |
| `ons-retail-sales-rap/` | Retail Sales Index | Quarto statistical summary | API metadata, raw/processed separation, tests, chart/table outputs |
| `uk-housing-affordability-monitor/` | House-price-to-earnings ratios | Quarto website | multi-source processing, transparent filters, methodology and limitations |
| `uk-inflation-monitor/` | CPIH inflation | Static HTML summary | time-series API fetch, latest-period calculation, offline validation |
| `uk-gdp-release-summary/` | GDP index | Static HTML release summary | previous-period growth calculation, revisions caveat, run metadata |
| `uk-population-change-explorer/` | UK population estimates | Static HTML explorer | area-period validation, positive count checks, derived population change |

See [`docs/project-comparison.md`](docs/project-comparison.md) for a fuller comparison.

## What The Repo Demonstrates

- Fetching official data from public ONS endpoints rather than relying on manual downloads.
- Separating raw data, processed data, analysis outputs, and publication files.
- Documenting methodology, assumptions, caveats, and known limitations.
- Running automated validation or tests before publication.
- Publishing reproducible outputs through GitHub Actions and GitHub Pages.
- Using source metadata and repeatable commands so the same output can be rebuilt after a new statistical release.

## Reusing The Pattern

For a new GSS RAP, start with the guidance in:

- [`docs/reusable-rap-pattern.md`](docs/reusable-rap-pattern.md): suggested project structure, commands, pipeline stages, and automation pattern.
- [`docs/rap-quality-checklist.md`](docs/rap-quality-checklist.md): quality assurance checklist mapped to reproducible official-statistics production.
- [`docs/project-comparison.md`](docs/project-comparison.md): which examples are useful for different design choices.
- [`template/`](template/): a minimal copyable RAP starter with standard commands, validation, and run metadata.
- [`docs/adapt-for-your-statistic.md`](docs/adapt-for-your-statistic.md): practical steps for adapting the pattern to a new statistic.
- [`docs/production-readiness-matrix.md`](docs/production-readiness-matrix.md): what the examples demonstrate and what production teams still need to add.
- [`docs/run-metadata-schema.md`](docs/run-metadata-schema.md): shared `run-metadata.json` field definitions.
- [`docs/ci-examples/`](docs/ci-examples/): example GitHub Actions workflows for offline tests, live integration checks, and controlled publication builds.

A minimal RAP should normally include:

1. A documented source-data acquisition step.
2. Raw source files or source metadata that can be audited.
3. A deterministic transform from raw data to analytical data.
4. Automated checks for schema, missingness, duplicates, date coverage, and expected values.
5. A clear publication output with methodology, limitations, and licence/source information.
6. A single command or workflow that rebuilds the output from source.

## Repository Structure

```text
.
├── docs/                                  # reusable GSS RAP guidance
├── template/                              # minimal copyable RAP starter
├── site/                                  # landing page for the unified GitHub Pages site
├── ons-retail-sales-rap/                  # Quarto RAP for Retail Sales Index
├── uk-housing-affordability-monitor/      # Quarto monitor for housing affordability
├── uk-labour-market-resilience-monitor/   # static dashboard for labour market indicators
├── uk-inflation-monitor/                  # static monitor for CPIH inflation
├── uk-gdp-release-summary/                # static summary for GDP index changes
└── uk-population-change-explorer/         # static explorer for population change
```

## Local Use

Each project has its own README with setup and run instructions. In general, the projects follow this shape:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then run the project-specific fetch, transform, validate, test, or report commands documented in the relevant project folder.

The repository also provides a shared command interface:

```bash
make install              # install dependencies for all projects
make validate             # validate existing generated outputs only
make test                 # run offline validation and unit tests
make integration-test     # refresh live ONS data and validate outputs
make build                # refresh live data and rebuild all reports/dashboards
make build-labour-market  # rebuild the labour market monitor
make build-retail-sales   # rebuild the retail sales report
make build-housing        # rebuild the housing affordability monitor
make build-inflation      # rebuild the inflation monitor
make build-gdp            # rebuild the GDP release summary
make build-population     # rebuild the population change explorer
make clean                # remove generated outputs
```

Each project implements the same Make targets where practical: `install`, `fetch`, `transform`, `validate`, `test`, `integration-test`, `report`, and `clean`. Some examples have combined fetch and transform stages because the source script currently performs both operations.

`make test` is intentionally offline: it validates existing generated outputs and runs local unit tests without calling public ONS endpoints. Use `make integration-test` when you want to refresh live source data before validation. Use `make build` for the full refresh and publication-build path.

## How To Verify This Repo

For local assurance without network dependency, run:

```bash
make test
```

For a live-source check, run:

```bash
make integration-test
```

For full publication outputs, run:

```bash
make build
```

The live-source and build targets require access to public ONS endpoints. Report targets that render Quarto outputs also require the Quarto CLI.

## Quality And Caveats

These examples are intentionally compact. They demonstrate production patterns, but they are not replacements for full departmental statistical production controls. Before using the pattern in a live official-statistics setting, teams should add the appropriate governance, peer review, accessibility testing, disclosure control, release management, and sign-off processes.

The examples use public ONS data. ONS content is available under the Open Government Licence unless otherwise stated by the source.
