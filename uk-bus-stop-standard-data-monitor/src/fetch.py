from __future__ import annotations

import json
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def fetch() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    raw_nptg_path = Path(config["paths"]["raw_nptg"])
    metadata_path = Path(config["paths"]["raw_metadata"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    fetched_sources = []
    for label, url, path in (
        ("naptan_access_nodes", config["source"]["url"], raw_path),
        ("nptg_gazetteer", config["source"]["nptg_url"], raw_nptg_path),
    ):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "uk-statistics-rap/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read()
            content_type = response.headers.get("Content-Type", "")
            etag = response.headers.get("ETag", "")
            last_modified = response.headers.get("Last-Modified", "")
            status = response.status
        path.write_bytes(body)
        fetched_sources.append(
            {
                "name": label,
                "source_url": url,
                "path": str(path),
                "status": status,
                "content_type": content_type,
                "etag": etag,
                "last_modified": last_modified,
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
            }
        )

    metadata_path.write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "sources": fetched_sources,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    fetch()
