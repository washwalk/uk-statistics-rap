from __future__ import annotations

import json
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

    manifest = {
        "raw_csv": ingest_result["csv_path"],
        "raw_metadata": ingest_result["metadata_path"],
        "clean_csv": clean_path,
        "summary_csv": summary_path,
        "chart_png": chart_path,
    }
    manifest_path = Path(config["paths"]["processed_dir"]) / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    outputs = run_pipeline()
    print(pd.Series(outputs).to_string())
