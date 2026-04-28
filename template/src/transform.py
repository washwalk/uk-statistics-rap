from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


def load_config() -> dict:
    return yaml.safe_load(Path("config.yml").read_text(encoding="utf-8"))


def transform() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    processed_path = Path(config["paths"]["processed_data"])
    run_metadata_path = Path(config["paths"]["run_metadata"])
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(raw_path)
    required_columns = config["required_columns"]
    analysis = frame.loc[:, required_columns].copy()
    analysis["period"] = pd.to_datetime(analysis["period"], errors="coerce").dt.date.astype(str)
    analysis["value"] = pd.to_numeric(analysis["value"], errors="coerce")
    analysis = analysis.sort_values(config["expected_grain"])
    analysis.to_csv(processed_path, index=False)

    run_metadata = {
        "project_name": config["project_name"],
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_urls": [config["source"]["url"]],
        "input_row_counts": {"raw_data": int(len(frame))},
        "output_row_counts": {"processed_data": int(len(analysis))},
        "outputs": {"processed_data": str(processed_path)},
        "validation_status": "not_run",
    }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    transform()
