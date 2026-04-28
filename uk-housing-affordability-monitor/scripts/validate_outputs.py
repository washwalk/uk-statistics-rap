from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def _read_csv(path: Path, errors: list[str]) -> pd.DataFrame:
    if not path.exists():
        errors.append(f"Missing output: {path}")
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if frame.empty:
        errors.append(f"Output is empty: {path}")
    return frame


def _require_columns(frame: pd.DataFrame, path: Path, columns: set[str], errors: list[str]) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        errors.append(f"{path} missing columns: {sorted(missing)}")


def validate_outputs() -> None:
    errors: list[str] = []

    by_area_path = DATA_DIR / "affordability_by_area.csv"
    trend_path = DATA_DIR / "affordability_trend.csv"
    least_path = DATA_DIR / "least_affordable_latest.csv"
    most_path = DATA_DIR / "most_affordable_latest.csv"
    metadata_path = DATA_DIR / "metadata.json"
    run_metadata_path = DATA_DIR / "run-metadata.json"

    by_area = _read_csv(by_area_path, errors)
    trend = _read_csv(trend_path, errors)
    least = _read_csv(least_path, errors)
    most = _read_csv(most_path, errors)

    _require_columns(
        by_area,
        by_area_path,
        {"year", "area_code", "area_name", "median_house_price", "median_annual_pay", "affordability_ratio"},
        errors,
    )
    _require_columns(trend, trend_path, {"year", "affordability_ratio"}, errors)
    _require_columns(least, least_path, {"area_name", "affordability_ratio"}, errors)
    _require_columns(most, most_path, {"area_name", "affordability_ratio"}, errors)

    if "affordability_ratio" in by_area.columns:
        ratios = pd.to_numeric(by_area["affordability_ratio"], errors="coerce")
        if ratios.isna().any():
            errors.append("Affordability ratios contain non-numeric values")
        if (ratios <= 0).any():
            errors.append("Affordability ratios must be positive")

    if {"year", "area_code"}.issubset(by_area.columns) and by_area.duplicated(["year", "area_code"]).any():
        errors.append("Area output contains duplicate year and area_code rows")

    if not metadata_path.exists():
        errors.append(f"Missing output: {metadata_path}")
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        for key in ("generated_at", "latest_year", "area_count_latest", "sources"):
            if key not in metadata:
                errors.append(f"Metadata missing key: {key}")

    if not run_metadata_path.exists():
        errors.append(f"Missing output: {run_metadata_path}")
    else:
        run_metadata = json.loads(run_metadata_path.read_text(encoding="utf-8"))
        required = {
            "project_name",
            "run_timestamp",
            "source_urls",
            "input_row_counts",
            "output_row_counts",
            "outputs",
            "validation_status",
        }
        missing = required.difference(run_metadata)
        if missing:
            errors.append(f"Run metadata missing keys: {sorted(missing)}")
        if not run_metadata.get("source_urls"):
            errors.append("Run metadata source_urls is empty")
        for count_name, count in run_metadata.get("output_row_counts", {}).items():
            if not isinstance(count, int) or count <= 0:
                errors.append(f"Run metadata output row count is invalid for {count_name}: {count}")

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))

    print("Validation passed")


if __name__ == "__main__":
    validate_outputs()
