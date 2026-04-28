from __future__ import annotations

import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = {"period", "period_type", "measure", "value", "change_from_previous", "source_series"}
REQUIRED_METADATA = {"project_name", "run_timestamp", "source_urls", "input_row_counts", "output_row_counts", "outputs", "validation_status"}
MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def monthly_period_key(period: str) -> tuple[int, int] | None:
    parts = period.split()
    if len(parts) != 2 or parts[1] not in MONTHS:
        return None
    try:
        return int(parts[0]), MONTHS[parts[1]]
    except ValueError:
        return None


def validate() -> None:
    config = load_config()
    errors: list[str] = []
    rows: list[dict] = []
    metadata: dict = {}
    processed_path = Path(config["paths"]["processed_data"])
    metadata_path = Path(config["paths"]["run_metadata"])

    if not processed_path.exists():
        errors.append(f"Missing processed data: {processed_path}")
    else:
        with processed_path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            errors.append(f"Processed data missing columns: {sorted(missing)}")
        if not rows:
            errors.append("Processed data is empty")
        keys = [(row["period"], row["measure"]) for row in rows]
        if len(keys) != len(set(keys)):
            errors.append("Processed data contains duplicate period-measure rows")
        period_keys: list[tuple[int, int]] = []
        for row in rows:
            if not row["period"]:
                errors.append("Processed data contains a blank period")
            period_key = monthly_period_key(row["period"])
            if row.get("period_type") != "months":
                errors.append(f"Unexpected period type for period {row.get('period')}")
            if period_key is None:
                errors.append(f"Period is not in expected monthly format for period {row.get('period')}")
            else:
                period_keys.append(period_key)
            if row.get("measure") != config["source"]["measure"]:
                errors.append(f"Unexpected measure for period {row.get('period')}")
            if row["source_series"] != config["source"]["series_id"]:
                errors.append(f"Unexpected source series for period {row.get('period')}")
            try:
                float(row["value"])
            except ValueError:
                errors.append(f"Value is not numeric for period {row.get('period')}")
            if row["change_from_previous"]:
                try:
                    float(row["change_from_previous"])
                except ValueError:
                    errors.append(f"Change is not numeric for period {row.get('period')}")
        if period_keys and period_keys != sorted(period_keys):
            errors.append("Processed data periods are not sorted ascending")
        if not any(row["change_from_previous"] for row in rows[1:]):
            errors.append("No previous-period changes were calculated")

    if not metadata_path.exists():
        errors.append(f"Missing run metadata: {metadata_path}")
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        missing = REQUIRED_METADATA.difference(metadata)
        if missing:
            errors.append(f"Run metadata missing keys: {sorted(missing)}")
        if metadata.get("project_name") != config["project_name"]:
            errors.append("Run metadata project name does not match config")
        if config["source"]["url"] not in metadata.get("source_urls", []):
            errors.append("Run metadata does not include configured source URL")
        if metadata.get("output_row_counts", {}).get("processed_data") != len(rows):
            errors.append("Run metadata processed row count does not match output")
        if metadata.get("outputs", {}).get("processed_data") != str(processed_path):
            errors.append("Run metadata processed output path does not match config")
        if metadata.get("outputs", {}).get("report") != config["paths"]["report"]:
            errors.append("Run metadata report output path does not match config")
        if metadata.get("validation_status") not in {"not_run", "passed"}:
            errors.append("Run metadata validation status must be not_run or passed")

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    if metadata_path.exists() and metadata:
        metadata["validation_status"] = "passed"
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print("Validation passed")


if __name__ == "__main__":
    validate()
