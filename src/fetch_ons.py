from __future__ import annotations

import json
from datetime import datetime, timezone

import requests

from config import ONS_BASE_URL, RAW_DIR, SERIES


def fetch_series() -> list[dict[str, str]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for item in SERIES:
        url = f"{ONS_BASE_URL}/{item['path']}"
        response = requests.get(url, timeout=30, headers={"User-Agent": "uk-labour-market-resilience-monitor/1.0"})
        response.raise_for_status()
        payload = response.json()

        output_path = RAW_DIR / f"{item['id']}.json"
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        manifest.append(
            {
                "id": item["id"],
                "title": item["title"],
                "url": url,
                "raw_file": str(output_path.relative_to(RAW_DIR.parents[1])),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    fetched = fetch_series()
    print(f"Fetched {len(fetched)} ONS time series")
