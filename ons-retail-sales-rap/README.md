# ONS Retail Sales RAP

[![Publish Statistical Report](https://github.com/washwalk/ons-retail-sales-rap/actions/workflows/publish-report.yml/badge.svg)](https://github.com/washwalk/ons-retail-sales-rap/actions/workflows/publish-report.yml)

Automated reproducible analytical pipeline using Python and Quarto to ingest ONS Retail Sales Index data, clean and analyse it, and generate a statistical summary report.

Published report: `https://washwalk.github.io/ons-retail-sales-rap/`

## Purpose

This project demonstrates a Reproducible Analytical Pipeline (RAP) for statistical bulletin production. It pulls the latest available data from the public ONS API, preserves the raw data, creates a clean analytical dataset, produces headline statistics and charts, and renders a formatted report.

The pipeline is designed so that when a new monthly release is published, the report can be regenerated with a single command.

## Data Source

- Dataset: ONS Retail Sales Index
- API dataset ID: `retail-sales-index`
- Release frequency: monthly
- Source: `https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index`

## Quick Start

Prerequisites:

- Python 3.10 or later with `pip`
- Quarto CLI: `https://quarto.org/docs/get-started/`

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the data pipeline only:

```bash
make pipeline
```

Generate the full report:

```bash
make report
```

If your system only exposes Python as `python3`, use the provided `Makefile`; it calls `python3` directly.

Run tests:

```bash
make test
```

## Outputs

- Raw ONS CSV and metadata: `data/raw/`
- Clean analytical dataset: `data/processed/retail_sales_index_clean.csv`
- Headline summary table: `outputs/tables/headline_summary.csv`
- Trend chart: `outputs/figures/retail_sales_index_trend.png`
- Quarto HTML report: `outputs/statistical_summary.html`

Generated data and reports are excluded from git because they can be recreated from the source code.

## Automated Publishing

GitHub Actions runs the full RAP on every push to `main`, on manual dispatch, and on a monthly schedule. The workflow installs Python dependencies and Quarto, rebuilds the report from the latest ONS data, and publishes the generated HTML to GitHub Pages.

This provides an auditable run history and a public report URL while keeping generated data out of version control.

## RAP Features

- Public API ingestion rather than manual downloads.
- Raw and processed data are stored separately.
- Repeatable cleaning and analysis steps.
- One-command report generation through `make report`.
- Automated GitHub Pages publication through GitHub Actions.
- Lightweight automated tests for core transformations.
- Version-control friendly project structure.

## Interview Summary

This RAP reduces manual handling and improves reproducibility, auditability, and transparency. The code resolves the latest ONS release dynamically, so the same pipeline can be rerun after each monthly publication to produce an updated statistical summary.
