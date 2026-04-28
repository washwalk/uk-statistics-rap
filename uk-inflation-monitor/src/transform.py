from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def source_points(payload: dict) -> tuple[str, list[dict]]:
    for period_type in ("months", "quarters", "years"):
        points = payload.get(period_type) or []
        if points:
            return period_type, points
    raise ValueError("Source payload did not contain months, quarters, or years")


def build_rows(config: dict, payload: dict) -> list[dict]:
    period_type, points = source_points(payload)
    rows: list[dict] = []
    previous_value: float | None = None
    for point in points:
        value_text = str(point.get("value", "")).strip()
        if not value_text:
            continue
        value = float(value_text)
        change = "" if previous_value is None else round(value - previous_value, 3)
        rows.append(
            {
                "period": point.get("date"),
                "period_type": period_type,
                "measure": config["source"]["measure"],
                "value": value,
                "change_from_previous": change,
                "source_series": config["source"]["series_id"],
            }
        )
        previous_value = value
    if not rows:
        raise ValueError("No valid source points were available to transform")
    return rows


def transform() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    processed_path = Path(config["paths"]["processed_data"])
    run_metadata_path = Path(config["paths"]["run_metadata"])
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    _, points = source_points(payload)
    rows = build_rows(config, payload)

    with processed_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    run_metadata_path.write_text(
        json.dumps(
            {
                "project_name": config["project_name"],
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_urls": [config["source"]["url"]],
                "input_row_counts": {"source_points": len(points)},
                "output_row_counts": {"processed_data": len(rows)},
                "outputs": {"processed_data": str(processed_path), "report": config["paths"]["report"]},
                "validation_status": "not_run",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    transform()
