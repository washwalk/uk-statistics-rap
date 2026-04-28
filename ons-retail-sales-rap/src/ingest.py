from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

USER_AGENT = "ons-retail-sales-rap/0.1"


def fetch_json(url: str) -> dict[str, Any]:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    return response.json()


def get_latest_version_metadata(config: dict[str, Any]) -> dict[str, Any]:
    dataset_url = f"{config['api_base_url']}/datasets/{config['dataset_id']}"
    dataset_metadata = fetch_json(dataset_url)
    latest_url = dataset_metadata["links"]["latest_version"]["href"]
    version_metadata = fetch_json(latest_url)
    version_metadata["dataset_metadata"] = dataset_metadata
    return version_metadata


def download_latest_csv(config: dict[str, Any]) -> dict[str, str]:
    metadata = get_latest_version_metadata(config)
    csv_url = metadata["downloads"]["csv"]["href"]
    raw_dir = Path(config["paths"]["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    version = str(metadata["version"])
    csv_path = raw_dir / f"{config['dataset_id']}_v{version}.csv"
    metadata_path = raw_dir / f"{config['dataset_id']}_v{version}_metadata.json"

    response = requests.get(csv_url, headers={"User-Agent": USER_AGENT}, timeout=180)
    response.raise_for_status()
    csv_path.write_bytes(response.content)

    run_metadata = {
        "dataset_id": config["dataset_id"],
        "dataset_title": metadata["dataset_metadata"].get("title", config["dataset_id"]),
        "version": version,
        "release_date": metadata.get("release_date", ""),
        "download_url": csv_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "latest_version_url": metadata["links"]["self"]["href"],
    }
    metadata_path.write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")

    return {
        "csv_path": str(csv_path),
        "metadata_path": str(metadata_path),
        **run_metadata,
    }
