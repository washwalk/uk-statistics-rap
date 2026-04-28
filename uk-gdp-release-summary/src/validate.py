from __future__ import annotations

import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = {"period", "period_type", "measure", "value", "growth_from_previous_percent", "source_series"}
REQUIRED_METADATA = {"project_name", "run_timestamp", "source_urls", "input_row_counts", "output_row_counts", "outputs", "validation_status"}


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def validate() -> None:
    config = load_config()
    errors: list[str] = []
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
        for row in rows:
            try:
                float(row["value"])
            except ValueError:
                errors.append(f"Value is not numeric for period {row.get('period')}")
        if not any(row["growth_from_previous_percent"] for row in rows[1:]):
            errors.append("No previous-period growth rates were calculated")
    if not metadata_path.exists():
        errors.append(f"Missing run metadata: {metadata_path}")
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        missing = REQUIRED_METADATA.difference(metadata)
        if missing:
            errors.append(f"Run metadata missing keys: {sorted(missing)}")
    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    print("Validation passed")


if __name__ == "__main__":
    validate()
