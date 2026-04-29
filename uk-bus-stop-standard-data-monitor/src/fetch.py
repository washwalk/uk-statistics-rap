from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def fetch() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    metadata_path = Path(config["paths"]["raw_metadata"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        config["source"]["url"],
        headers={"User-Agent": "uk-statistics-rap/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")

    raw_path.write_bytes(body)
    metadata_path.write_text(
        json.dumps(
            {
                "source_url": config["source"]["url"],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "content_type": content_type,
                "bytes": len(body),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    fetch()
