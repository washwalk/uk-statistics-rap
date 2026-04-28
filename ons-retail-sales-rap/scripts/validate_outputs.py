from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed")
OUTPUTS_DIR = Path("outputs")


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


def _validate_run_metadata(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing output: {path}")
        return

    metadata = json.loads(path.read_text(encoding="utf-8"))
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


def validate_outputs() -> None:
    errors: list[str] = []

    clean_path = PROCESSED_DIR / "retail_sales_index_clean.csv"
    manifest_path = PROCESSED_DIR / "manifest.json"
    metadata_path = PROCESSED_DIR / "run-metadata.json"
    summary_path = OUTPUTS_DIR / "tables" / "headline_summary.csv"
    chart_path = OUTPUTS_DIR / "figures" / "retail_sales_index_trend.png"

    clean = _read_csv(clean_path, errors)
    summary = _read_csv(summary_path, errors)

    _require_columns(
        clean,
        clean_path,
        {
            "period",
            "time",
            "geography_code",
            "geography_name",
            "industry",
            "prices",
            "seasonal_adjustment",
            "value",
        },
        errors,
    )
    _require_columns(
        summary,
        summary_path,
        {"latest_period", "latest_value", "month_on_month_change", "year_on_year_change", "observations"},
        errors,
    )

    if "period" in clean.columns:
        periods = pd.to_datetime(clean["period"], errors="coerce")
        if periods.isna().any():
            errors.append("Clean retail data contains invalid periods")
        if periods.duplicated().any():
            errors.append("Clean retail data contains duplicate periods")
        if not periods.is_monotonic_increasing:
            errors.append("Clean retail data periods are not sorted")

    if "value" in clean.columns:
        values = pd.to_numeric(clean["value"], errors="coerce")
        if values.isna().any():
            errors.append("Clean retail data contains non-numeric values")
        if (values <= 0).any():
            errors.append("Clean retail index values must be positive")

    if not manifest_path.exists():
        errors.append(f"Missing output: {manifest_path}")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in ("raw_csv", "raw_metadata", "clean_csv", "summary_csv", "chart_png", "run_metadata"):
            if key not in manifest:
                errors.append(f"Manifest missing key: {key}")

    if not chart_path.exists():
        errors.append(f"Missing output: {chart_path}")

    _validate_run_metadata(metadata_path, errors)

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))

    print("Validation passed")


if __name__ == "__main__":
    validate_outputs()
