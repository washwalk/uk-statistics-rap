from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


MONTH_FORMATS = ("%b-%y", "%Y %b", "%Y-%m", "%b %Y")


def _normalise_column_name(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
    )


def _parse_period(value: object) -> pd.Timestamp:
    text = str(value).strip()
    for fmt in MONTH_FORMATS:
        try:
            parsed = pd.to_datetime(text, format=fmt)
            if fmt == "%b-%y" and parsed.year > pd.Timestamp.today().year + 1:
                parsed = parsed - pd.DateOffset(years=100)
            return parsed
        except ValueError:
            continue
    return pd.to_datetime(text, errors="coerce")


def _find_value_column(columns: list[str]) -> str:
    candidates = ["v4_1", "v4_0", "value", "observation", "obs_value"]
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"Could not identify value column. Available columns: {columns}")


def clean_retail_sales_data(raw_csv_path: str, config: dict[str, Any]) -> pd.DataFrame:
    raw = pd.read_csv(raw_csv_path)
    raw.columns = [_normalise_column_name(column) for column in raw.columns]

    value_column = _find_value_column(list(raw.columns))
    required = {
        "time",
        "countries",
        "geography",
        "unofficialstandardindustrialclassification",
        "prices",
        "seasonaladjustment",
    }
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"Raw data missing required columns: {sorted(missing)}")

    headline = config["headline_series"]
    data = raw.copy()
    data["value"] = pd.to_numeric(data[value_column], errors="coerce")
    data["period"] = data["time"].map(_parse_period)

    filtered = data[
        (data["countries"] == headline["geography"])
        & data["unofficialstandardindustrialclassification"].str.contains(
            headline["industry_label_contains"], case=False, na=False, regex=False
        )
        & data["prices"].str.contains(headline["prices_label_contains"], case=False, na=False, regex=False)
        & data["seasonaladjustment"].str.contains(
            headline["seasonal_adjustment_label_contains"], case=False, na=False, regex=False
        )
    ].copy()

    if filtered.empty:
        raise ValueError("Headline Retail Sales Index series filter returned no rows.")

    cleaned = filtered[
        [
            "period",
            "time",
            "countries",
            "geography",
            "unofficialstandardindustrialclassification",
            "prices",
            "seasonaladjustment",
            "value",
        ]
    ].rename(
        columns={
            "countries": "geography_code",
            "geography": "geography_name",
            "unofficialstandardindustrialclassification": "industry",
            "seasonaladjustment": "seasonal_adjustment",
        }
    )

    cleaned = cleaned.dropna(subset=["period", "value"]).sort_values("period").reset_index(drop=True)
    cleaned["month_on_month_change"] = cleaned["value"].diff()
    cleaned["year_on_year_change"] = cleaned["value"].diff(12)

    return cleaned


def write_clean_data(cleaned: pd.DataFrame, config: dict[str, Any]) -> str:
    processed_dir = Path(config["paths"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "retail_sales_index_clean.csv"
    cleaned.to_csv(output_path, index=False)
    return str(output_path)
