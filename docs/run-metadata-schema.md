# Run Metadata Schema

Each RAP example writes a lightweight `run-metadata.json` file. The file is intended to help analysts, reviewers, and automated workflows understand what source data were used, what outputs were created, and whether validation has run.

## Required Fields

| Field | Type | Description |
| --- | --- | --- |
| `project_name` | string | Stable project or output identifier. |
| `run_timestamp` | string | ISO 8601 timestamp for the pipeline run, preferably UTC. |
| `source_urls` | array of strings | Source API endpoints, CSV URLs, metadata URLs, or publication URLs used by the run. |
| `input_row_counts` | object | Row counts or observation counts for raw/source inputs. |
| `output_row_counts` | object | Row counts for processed datasets, tables, or site data. |
| `outputs` | object | Paths or identifiers for generated outputs. |
| `validation_status` | string | Current validation state, such as `not_run`, `passed`, or `failed`. |

## Recommended Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| `source_version` | string | Source dataset version, edition, or release identifier. |
| `release_date` | string | Source release date where available. |
| `filters_applied` | object | Geography, measure, seasonal adjustment, date, or population filters. |
| `code_version` | string | Git commit SHA or release tag used to build the output. |
| `dependency_snapshot` | object | Key package versions or lockfile reference. |
| `validation_errors` | array of strings | Validation errors if validation failed. |

## Example

```json
{
  "project_name": "example-statistical-rap",
  "run_timestamp": "2026-04-28T12:30:00+00:00",
  "source_urls": [
    "https://example.gov.uk/source-data.csv"
  ],
  "input_row_counts": {
    "source_data": 1200
  },
  "output_row_counts": {
    "analysis.csv": 960,
    "summary.csv": 12
  },
  "outputs": {
    "processed_data": "data/processed/analysis.csv",
    "summary_table": "outputs/tables/summary.csv",
    "report": "outputs/report.html"
  },
  "validation_status": "passed"
}
```

## Validation Guidance

Validation scripts should check that:

- all required fields are present
- `source_urls` is not empty
- row counts are positive integers where outputs are expected to be non-empty
- listed output paths exist where practical
- `run_timestamp` can be parsed as a timestamp

For a production pipeline, consider validating this file with JSON Schema and including the current Git commit SHA.
