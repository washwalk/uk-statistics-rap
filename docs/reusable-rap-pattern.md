# Reusable RAP Pattern

This pattern describes a small but complete reproducible analytical pipeline for a GSS-style statistical output. It is intended as a starting point, not a mandatory structure. A copyable starter is available in [`../template/`](../template/).

## Suggested Structure

```text
example-statistical-rap/
├── README.md
├── requirements.txt
├── config.yml
├── src/
│   ├── fetch.py
│   ├── transform.py
│   ├── validate.py
│   └── publish.py
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── figures/
│   └── tables/
└── reports/
```

## Standard Pipeline Stages

| Stage | Purpose | Typical output |
| --- | --- | --- |
| Fetch | Retrieve source data and metadata from official sources | raw CSV, JSON, metadata manifest |
| Transform | Convert source data into tidy analytical datasets | processed CSV or Parquet |
| Validate | Check source and processed data before publication | pass/fail log or validation report |
| Analyse | Calculate headline statistics, tables, and charts | tables, figures, summary data |
| Publish | Render the public-facing product | HTML report, dashboard, or website |

## Recommended Commands

Use consistent commands so analysts and reviewers can move between projects easily.

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

If a project does not use `make`, document equivalent Python commands in the README.

This repository now exposes those commands at the root level as well:

```bash
make test
make integration-test
make build
make build-labour-market
make build-retail-sales
make build-housing
make build-inflation
make build-gdp
make build-population
```

The root commands are thin wrappers around each project. This keeps project logic local while giving reviewers and users one predictable interface.

In this repository, `make test` is offline and validates existing generated outputs. `make integration-test` refreshes live public ONS data before validation. `make build` performs the full refresh and publication-build path.

## Configuration

Keep source IDs, URLs, geography filters, series IDs, and output paths in configuration where practical. This makes statistical choices easier to review and reduces the risk of hidden assumptions in code.

Useful configuration fields include:

- source dataset IDs and API base URLs
- expected geography or population coverage
- filter labels and codes
- publication title and output paths
- expected columns and units
- quality thresholds, such as permitted missingness or revision tolerances

## Run Metadata

For production-style use, write a machine-readable run metadata file during each build.

Required fields used by these examples:

- `project_name`
- `run_timestamp`
- `source_urls`
- `input_row_counts`
- `output_row_counts`
- `outputs`
- `validation_status`

Production teams may also add code version or commit SHA, source release dates, filters applied, and dependency versions. Each example now writes a lightweight `run-metadata.json` alongside its processed outputs. See [`run-metadata-schema.md`](run-metadata-schema.md) for the shared field definitions.

## Validation Rules

Start with simple checks and add domain-specific checks as risks become clear.

Common checks include:

- input files exist and are non-empty
- required columns are present
- values have expected types and units
- period fields parse and sort correctly
- key columns are unique where required
- joins do not unexpectedly drop records
- latest-period values are not stale
- publication outputs are generated

## Testing Strategy

Tests should focus on logic that would create a wrong statistic if it failed.

Good candidates for tests include:

- filter selection for headline series
- date and period parsing
- percentage or index change calculations
- joins across sources
- missing-data handling
- generation of summary tables used in publication

## Automation Pattern

A basic GitHub Actions workflow should usually:

1. Check out the repository.
2. Install Python and any report-rendering tools.
3. Install dependencies.
4. Run tests.
5. Fetch or restore source data.
6. Transform and validate data.
7. Render the report or dashboard.
8. Publish only after validation passes.

Scheduled refreshes are useful for recurring source releases, but teams should consider whether automated publication or manual sign-off is appropriate for their output.

Example GitHub Actions workflow templates are provided in [`ci-examples/`](ci-examples/). They are documented examples rather than active workflows so teams can adapt them before enabling automation.

## Documentation Needed For Reuse

Each RAP should explain:

- what user need the output serves
- what source data are used
- how the source data are filtered and transformed
- what the main statistical caveats are
- how to run the pipeline locally
- how the automated workflow publishes or prepares the output
- who owns the output and how issues should be raised
