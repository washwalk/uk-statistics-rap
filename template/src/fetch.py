from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


def load_config() -> dict:
    return yaml.safe_load(Path("config.yml").read_text(encoding="utf-8"))


def fetch() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    metadata_path = Path(config["paths"]["raw_metadata"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    source_url = config["source"]["url"]
    frame = pd.read_csv(source_url)
    frame.to_csv(raw_path, index=False)

    metadata = {
        "project_name": config["project_name"],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "source_name": config["source"]["name"],
        "input_rows": int(len(frame)),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    fetch()
