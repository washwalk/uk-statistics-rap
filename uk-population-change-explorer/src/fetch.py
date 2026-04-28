from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def fetch() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    metadata_path = Path(config["paths"]["raw_metadata"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    source_url = config["source"]["url"]
    request = Request(source_url, headers={"User-Agent": "uk-statistics-rap/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "project_name": config["project_name"],
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "source_url": source_url,
                "source_name": config["source"]["name"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    fetch()
