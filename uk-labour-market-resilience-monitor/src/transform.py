from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

from config import DOCS_DATA_DIR, PROCESSED_DIR, RAW_DIR, SERIES


def _observations(payload: dict) -> list[dict]:
    months = payload.get("months") or []
    quarters = payload.get("quarters") or []
    years = payload.get("years") or []
    return months or quarters or years


def _to_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _period_key(row: dict) -> str:
    return str(row.get("date") or row.get("label") or row.get("year") or "")


def transform() -> dict:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    latest_rows: list[dict] = []

    for item in SERIES:
        raw_path = RAW_DIR / f"{item['id']}.json"
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        observations = _observations(payload)
        rows = []

        for obs in observations:
            value = _to_float(obs.get("value"))
            if value is None:
                continue
            row = {
                "indicator_id": item["id"],
                "indicator": item["title"],
                "period": _period_key(obs),
                "value": value,
                "unit": item["unit"],
                "kind": item["kind"],
                "series_id": item["series_id"].upper(),
                "source_url": f"https://www.ons.gov.uk/{item['path']}",
            }
            rows.append(row)

        if not rows:
            raise ValueError(f"No numeric observations found for {item['id']}")

        latest = rows[-1].copy()
        previous = rows[-2]["value"] if len(rows) > 1 else None
        latest["previous_value"] = previous
        latest["change"] = None if previous is None else latest["value"] - previous
        latest["direction"] = item["direction"]
        latest["summary"] = item["summary"]
        latest_rows.append(latest)
        all_rows.extend(rows)

    csv_path = PROCESSED_DIR / "labour_market_indicators.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    latest_path = PROCESSED_DIR / "latest_snapshot.json"
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "indicators": latest_rows,
    }
    latest_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    site_payload = {
        "generated_at": snapshot["generated_at"],
        "series": all_rows,
        "latest": latest_rows,
    }
    (DOCS_DATA_DIR / "indicators.json").write_text(json.dumps(site_payload, indent=2), encoding="utf-8")
    return site_payload


if __name__ == "__main__":
    payload = transform()
    print(f"Processed {len(payload['series'])} observations across {len(payload['latest'])} indicators")
