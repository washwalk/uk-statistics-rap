from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"

ONS_BASE_URL = "https://www.ons.gov.uk"

SERIES = [
    {
        "id": "employment_rate",
        "title": "Employment rate",
        "series_id": "lf24",
        "dataset": "lms",
        "path": "employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/lf24/lms/data",
        "unit": "%",
        "kind": "rate",
        "direction": "higher_is_better",
        "summary": "Share of people aged 16 to 64 in employment.",
    },
    {
        "id": "unemployment_rate",
        "title": "Unemployment rate",
        "series_id": "mgsx",
        "dataset": "lms",
        "path": "employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsx/lms/data",
        "unit": "%",
        "kind": "rate",
        "direction": "lower_is_better",
        "summary": "Share of economically active people who are unemployed.",
    },
    {
        "id": "economic_inactivity_rate",
        "title": "Economic inactivity rate",
        "series_id": "lf2s",
        "dataset": "lms",
        "path": "employmentandlabourmarket/peoplenotinwork/economicinactivity/timeseries/lf2s/lms/data",
        "unit": "%",
        "kind": "rate",
        "direction": "lower_is_better",
        "summary": "Share of people aged 16 to 64 who are economically inactive.",
    },
    {
        "id": "vacancies",
        "title": "Vacancies",
        "series_id": "ap2y",
        "dataset": "unem",
        "path": "employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/ap2y/unem/data",
        "unit": "thousands",
        "kind": "count",
        "direction": "context",
        "summary": "Number of vacancies in the UK economy.",
    },
    {
        "id": "regular_pay_growth",
        "title": "Regular pay growth",
        "series_id": "kac3",
        "dataset": "lms",
        "path": "employmentandlabourmarket/peopleinwork/earningsandworkinghours/timeseries/kac3/lms/data",
        "unit": "%",
        "kind": "growth_rate",
        "direction": "higher_is_better",
        "summary": "Annual growth in average weekly earnings excluding bonuses.",
    },
]
