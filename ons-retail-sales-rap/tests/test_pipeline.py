import pandas as pd

from src.analyse import build_summary
from src.clean import clean_retail_sales_data


def test_build_summary_calculates_latest_changes():
    data = pd.DataFrame(
        {
            "period": pd.date_range("2024-01-01", periods=13, freq="MS"),
            "value": list(range(100, 113)),
        }
    )

    summary = build_summary(data)

    assert summary["latest_value"] == 112.0
    assert summary["month_on_month_change"] == 1.0
    assert summary["year_on_year_change"] == 12.0


def test_clean_retail_sales_data_filters_headline_series(tmp_path):
    raw_path = tmp_path / "raw.csv"
    pd.DataFrame(
        {
            "time": ["Jan-24", "Feb-24", "Jan-24"],
            "countries": ["K03000001", "K03000001", "K02000001"],
            "geography": ["Great Britain", "Great Britain", "United Kingdom"],
            "unofficialstandardindustrialclassification": [
                "All retailing including automotive fuel",
                "All retailing including automotive fuel",
                "All retailing including automotive fuel",
            ],
            "prices": ["Chained volume of retail sales", "Chained volume of retail sales", "Chained volume of retail sales"],
            "seasonaladjustment": ["Seasonally Adjusted", "Seasonally Adjusted", "Seasonally Adjusted"],
            "v4_1": [101.2, 102.4, 99.9],
        }
    ).to_csv(raw_path, index=False)

    config = {
        "headline_series": {
            "geography": "K03000001",
            "industry_label_contains": "All retailing including automotive fuel",
            "prices_label_contains": "Chained volume of retail sales",
            "seasonal_adjustment_label_contains": "Seasonally Adjusted",
        }
    }

    cleaned = clean_retail_sales_data(str(raw_path), config)

    assert len(cleaned) == 2
    assert set(["period", "value", "geography_code", "industry", "seasonal_adjustment"]).issubset(cleaned.columns)
