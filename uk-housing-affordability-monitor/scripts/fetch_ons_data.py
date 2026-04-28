"""Fetch ONS data and create housing affordability indicators.

The script deliberately discovers dataset versions from the ONS API rather than
hard-coding CSV release URLs. It then streams the CSV downloads so the GitHub
Actions workflow can refresh the monitor without storing raw data in git.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


API_BASE = "https://api.beta.ons.gov.uk/v1/datasets"
USER_AGENT = "uk-housing-affordability-monitor/1.0 (+https://github.com/washwalk/uk-housing-affordability-monitor)"
DATA_DIR = Path("data")


@dataclass(frozen=True)
class OnsDownload:
    dataset_id: str
    title: str
    release_date: str
    version_url: str
    csv_url: str


def get_json(url: str) -> dict:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    return response.json()


def download_from_version_url(dataset_id: str, title: str, version_url: str) -> OnsDownload:
    version = get_json(version_url)
    return OnsDownload(
        dataset_id=dataset_id,
        title=title,
        release_date=version.get("release_date", ""),
        version_url=version_url,
        csv_url=version["downloads"]["csv"]["href"],
    )


def latest_download(dataset_id: str) -> OnsDownload:
    dataset = get_json(f"{API_BASE}/{dataset_id}")
    return download_from_version_url(dataset_id, dataset["title"], dataset["links"]["latest_version"]["href"])


def downloads_for_editions(dataset_id: str, editions: set[int]) -> list[OnsDownload]:
    dataset = get_json(f"{API_BASE}/{dataset_id}")
    edition_index = get_json(dataset["links"]["editions"]["href"])
    downloads: list[OnsDownload] = []
    for item in edition_index["items"]:
        edition = item["edition"]
        if edition.isdigit() and int(edition) in editions:
            downloads.append(
                download_from_version_url(
                    dataset_id,
                    dataset["title"],
                    item["links"]["latest_version"]["href"],
                )
            )
    return sorted(downloads, key=lambda item: item.version_url)


def stream_csv_rows(url: str) -> Iterable[dict[str, str]]:
    with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=180) as response:
        response.raise_for_status()
        lines = (line.decode("utf-8-sig") for line in response.iter_lines() if line)
        yield from csv.DictReader(lines)


def number_or_none(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_house_prices(download: OnsDownload) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for row in stream_csv_rows(download.csv_url):
        if not (
            row["property-type"] == "all"
            and row["build-status"] == "all"
            and row["house-sales-and-prices"] == "median"
            and row["mmm"] == "sep"
        ):
            continue

        value = number_or_none(row["V4_1"])
        if value is None:
            continue

        records.append(
            {
                "year": int(row["Time"]),
                "area_code": row["administrative-geography"],
                "area_name": row["Geography"],
                "median_house_price": value,
            }
        )

    return pd.DataFrame.from_records(records)


def fetch_earnings(download: OnsDownload) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for row in stream_csv_rows(download.csv_url):
        value_key = next(key for key in row if key.lower().startswith("v4_"))
        if not (
            row["hours-and-earnings"] == "annual-pay-gross"
            and row["averages-and-percentiles"] == "median"
            and row["sex"] == "all"
            and row["working-pattern"] == "all"
            and row["workplace-or-residence"] == "residence"
        ):
            continue

        value = number_or_none(row[value_key])
        if value is None:
            continue

        records.append(
            {
                "year": int(row["Time"]),
                "area_code": row["administrative-geography"],
                "area_name": row["Geography"],
                "median_annual_pay": value,
            }
        )

    return pd.DataFrame.from_records(records)


def fetch_earnings_for_years(downloads: list[OnsDownload], years: set[int]) -> pd.DataFrame:
    frames = []
    for download in downloads:
        frame = fetch_earnings(download)
        frame = frame[frame["year"].isin(years)]
        if not frame.empty:
            frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=["year", "area_code", "area_name", "median_annual_pay"])
    return pd.concat(frames, ignore_index=True)


def area_type(area_code: str) -> str:
    if area_code.startswith(("E12", "W92")):
        return "region_or_country"
    if area_code.startswith(("E06", "E07", "E08", "E09", "W06")):
        return "local_authority"
    return "other"


def build_outputs() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    house_price_download = latest_download("house-prices-local-authority")
    house_prices = fetch_house_prices(house_price_download)
    house_price_years = set(int(year) for year in house_prices["year"].unique())
    earnings_downloads = downloads_for_editions("ashe-tables-7-and-8", house_price_years)
    earnings = fetch_earnings_for_years(earnings_downloads, house_price_years)

    affordability = house_prices.merge(
        earnings,
        on=["year", "area_code"],
        suffixes=("", "_earnings"),
        how="inner",
    )
    affordability["area_name"] = affordability["area_name"].fillna(affordability["area_name_earnings"])
    affordability = affordability.drop(columns=["area_name_earnings"])
    affordability["affordability_ratio"] = (
        affordability["median_house_price"] / affordability["median_annual_pay"]
    ).round(2)
    affordability["area_type"] = affordability["area_code"].map(area_type)
    affordability = affordability.sort_values(["year", "area_name"])

    latest_year = int(affordability["year"].max())
    latest = affordability.query("year == @latest_year and area_type == 'local_authority'").copy()
    national = (
        affordability.query("area_type == 'local_authority'")
        .groupby("year", as_index=False)
        .agg(
            median_house_price=("median_house_price", "median"),
            median_annual_pay=("median_annual_pay", "median"),
            affordability_ratio=("affordability_ratio", "median"),
        )
    )

    affordability.to_csv(DATA_DIR / "affordability_by_area.csv", index=False)
    national.to_csv(DATA_DIR / "affordability_trend.csv", index=False)
    latest.sort_values("affordability_ratio", ascending=False).head(20).to_csv(
        DATA_DIR / "least_affordable_latest.csv", index=False
    )
    latest.sort_values("affordability_ratio", ascending=True).head(20).to_csv(
        DATA_DIR / "most_affordable_latest.csv", index=False
    )

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "latest_year": latest_year,
        "area_count_latest": int(len(latest)),
        "median_ratio_latest": round(float(latest["affordability_ratio"].median()), 2),
        "least_affordable_area": latest.sort_values("affordability_ratio", ascending=False)
        .iloc[0][["area_name", "affordability_ratio"]]
        .to_dict(),
        "most_affordable_area": latest.sort_values("affordability_ratio", ascending=True)
        .iloc[0][["area_name", "affordability_ratio"]]
        .to_dict(),
        "sources": [house_price_download.__dict__, *[download.__dict__ for download in earnings_downloads]],
    }
    (DATA_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_outputs()
