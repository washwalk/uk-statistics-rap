from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def endpoint_url(url: str, api_key: str, limit: int = 100, offset: int = 0) -> str:
    params = {"api_key": api_key, "limit": str(limit), "offset": str(offset)}
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urllib.parse.urlencode(params)}"


def fetch_endpoint(label: str, url: str, api_key: str) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    pages: list[dict] = []
    offset = 0
    limit = 100
    while True:
        page_url = endpoint_url(url, api_key, limit=limit, offset=offset)
        request = urllib.request.Request(page_url, headers={"User-Agent": "uk-statistics-rap/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            etag = response.headers.get("ETag", "")
            last_modified = response.headers.get("Last-Modified", "")
        payload = json.loads(body.decode("utf-8"))
        if isinstance(payload, list):
            page_rows = payload
            next_url = None
        else:
            page_rows = payload.get("results", [])
            next_url = payload.get("next")
        rows.extend(page_rows)
        pages.append(
            {
                "name": label,
                "source_url": url,
                "status": status,
                "content_type": content_type,
                "etag": etag,
                "last_modified": last_modified,
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
                "offset": offset,
                "row_count": len(page_rows),
            }
        )
        if not next_url or len(page_rows) < limit:
            break
        offset += limit
    return rows, pages


def fetch_bods() -> None:
    api_key = os.environ.get("BODS_API_KEY", "").strip()
    if not api_key:
        print("BODS_API_KEY is not set; skipping BODS fetch")
        return

    config = load_config()
    paths = config["paths"]
    endpoints = config["bods"]["endpoints"]
    output_paths = {
        "timetables": Path(paths["raw_bods_timetables"]),
        "location_feeds": Path(paths["raw_bods_location_feeds"]),
        "fares": Path(paths["raw_bods_fares"]),
    }
    for path in output_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    fetched_sources = []
    for label, url in endpoints.items():
        rows, pages = fetch_endpoint(label, url, api_key)
        output_paths[label].write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        fetched_sources.extend(pages)

    Path(paths["raw_bods_metadata"]).write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "publisher": config["bods"]["publisher"],
                "coverage": config["bods"]["coverage"],
                "sources": fetched_sources,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    fetch_bods()
