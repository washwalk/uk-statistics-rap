from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml


def load_config() -> dict:
    return yaml.safe_load(Path("config.yml").read_text(encoding="utf-8"))


def validate() -> None:
    config = load_config()
    errors: list[str] = []
    processed_path = Path(config["paths"]["processed_data"])
    run_metadata_path = Path(config["paths"]["run_metadata"])

    if not processed_path.exists():
        errors.append(f"Missing processed data: {processed_path}")
    else:
        frame = pd.read_csv(processed_path)
        missing_columns = set(config["required_columns"]).difference(frame.columns)
        if missing_columns:
            errors.append(f"Processed data missing columns: {sorted(missing_columns)}")
        if frame.empty:
            errors.append("Processed data is empty")
        if frame.duplicated(config["expected_grain"]).any():
            errors.append(f"Processed data contains duplicate rows for {config['expected_grain']}")
        if "value" in frame.columns and pd.to_numeric(frame["value"], errors="coerce").isna().any():
            errors.append("Processed data contains non-numeric values")

    if not run_metadata_path.exists():
        errors.append(f"Missing run metadata: {run_metadata_path}")
    else:
        metadata = json.loads(run_metadata_path.read_text(encoding="utf-8"))
        required_metadata = {
            "project_name",
            "run_timestamp",
            "source_urls",
            "input_row_counts",
            "output_row_counts",
            "outputs",
            "validation_status",
        }
        missing_metadata = required_metadata.difference(metadata)
        if missing_metadata:
            errors.append(f"Run metadata missing keys: {sorted(missing_metadata)}")

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))

    print("Validation passed")


if __name__ == "__main__":
    validate()
