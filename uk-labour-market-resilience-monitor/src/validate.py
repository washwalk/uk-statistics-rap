from __future__ import annotations

import csv
import json

from config import DOCS_DATA_DIR, PROCESSED_DIR, RAW_DIR, SERIES


def validate() -> None:
    errors: list[str] = []

    for item in SERIES:
        raw_path = RAW_DIR / f"{item['id']}.json"
        if not raw_path.exists():
            errors.append(f"Missing raw file: {raw_path}")
            continue
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        if not any(payload.get(key) for key in ("months", "quarters", "years")):
            errors.append(f"Raw payload has no recognised observations: {item['id']}")

    csv_path = PROCESSED_DIR / "labour_market_indicators.csv"
    if not csv_path.exists():
        errors.append("Missing processed CSV")
    else:
        with csv_path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            errors.append("Processed CSV is empty")
        required = {"indicator_id", "indicator", "period", "value", "unit", "kind", "series_id", "source_url"}
        missing = required.difference(rows[0].keys()) if rows else required
        if missing:
            errors.append(f"Processed CSV missing columns: {sorted(missing)}")
        for row in rows:
            try:
                value = float(row["value"])
            except (KeyError, ValueError):
                errors.append(f"Non-numeric value in row: {row}")
                continue
            if row.get("kind") == "rate" and value < 0:
                errors.append(f"Negative percentage value in row: {row}")
            if not row.get("period"):
                errors.append(f"Missing period in row: {row}")
        keys = [(row.get("indicator_id"), row.get("period")) for row in rows]
        if len(keys) != len(set(keys)):
            errors.append("Processed CSV contains duplicate indicator_id and period rows")

    snapshot_path = PROCESSED_DIR / "latest_snapshot.json"
    if not snapshot_path.exists():
        errors.append("Missing latest snapshot JSON")
    else:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        indicators = snapshot.get("indicators", [])
        if len(indicators) != len(SERIES):
            errors.append(f"Expected {len(SERIES)} latest indicators, found {len(indicators)}")

    site_data_path = DOCS_DATA_DIR / "indicators.json"
    if not site_data_path.exists():
        errors.append("Missing site data JSON")

    metadata_path = PROCESSED_DIR / "run-metadata.json"
    if not metadata_path.exists():
        errors.append("Missing run metadata JSON")
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        required = {
            "project_name",
            "run_timestamp",
            "source_urls",
            "input_row_counts",
            "output_row_counts",
            "outputs",
            "validation_status",
        }
        missing = required.difference(metadata)
        if missing:
            errors.append(f"Run metadata missing keys: {sorted(missing)}")
        if not metadata.get("source_urls"):
            errors.append("Run metadata source_urls is empty")
        for count_name, count in metadata.get("output_row_counts", {}).items():
            if not isinstance(count, int) or count <= 0:
                errors.append(f"Run metadata output row count is invalid for {count_name}: {count}")

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))

    print("Validation passed")


if __name__ == "__main__":
    validate()
