from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from src.analyse import build_summary, write_summary_table, write_trend_chart
from src.clean import clean_retail_sales_data, write_clean_data
from src.ingest import download_latest_csv


def load_config(path: str = "config.yml") -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run_pipeline(config_path: str = "config.yml") -> dict[str, str]:
    config = load_config(config_path)
    ingest_result = download_latest_csv(config)
    cleaned = clean_retail_sales_data(ingest_result["csv_path"], config)
    clean_path = write_clean_data(cleaned, config)

    summary = build_summary(cleaned)
    summary.update(
        {
            "dataset_title": ingest_result["dataset_title"],
            "dataset_version": ingest_result["version"],
            "release_date": ingest_result["release_date"],
            "retrieved_at_utc": ingest_result["retrieved_at_utc"],
            "source_url": ingest_result["download_url"],
        }
    )
    summary_path = write_summary_table(summary, config)
    chart_path = write_trend_chart(cleaned, config)

    metadata_path = Path(config["paths"]["processed_dir"]) / "run-metadata.json"
    manifest = {
        "raw_csv": ingest_result["csv_path"],
        "raw_metadata": ingest_result["metadata_path"],
        "clean_csv": clean_path,
        "summary_csv": summary_path,
        "chart_png": chart_path,
        "run_metadata": str(metadata_path),
    }
    manifest_path = Path(config["paths"]["processed_dir"]) / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run_metadata = {
        "project_name": "ons-retail-sales-rap",
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_urls": [ingest_result["download_url"]],
        "source_version": ingest_result["version"],
        "release_date": ingest_result["release_date"],
        "input_row_counts": {"raw_csv": int(pd.read_csv(ingest_result["csv_path"]).shape[0])},
        "output_row_counts": {"clean_csv": int(len(cleaned)), "summary_csv": 1},
        "outputs": manifest,
        "validation_status": "not_run",
    }
    metadata_path.write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    outputs = run_pipeline()
    print(pd.Series(outputs).to_string())
