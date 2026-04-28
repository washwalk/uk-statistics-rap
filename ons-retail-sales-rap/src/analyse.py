from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


def build_summary(cleaned: pd.DataFrame) -> dict[str, Any]:
    if cleaned.empty:
        raise ValueError("Cannot summarise an empty dataset.")

    latest = cleaned.iloc[-1]
    previous = cleaned.iloc[-2] if len(cleaned) > 1 else latest
    previous_year = cleaned.iloc[-13] if len(cleaned) > 12 else latest

    mom_change = latest["value"] - previous["value"]
    yoy_change = latest["value"] - previous_year["value"]
    direction = "increased" if mom_change > 0 else "decreased" if mom_change < 0 else "was unchanged"

    return {
        "latest_period": latest["period"].strftime("%B %Y"),
        "latest_value": round(float(latest["value"]), 1),
        "previous_period": previous["period"].strftime("%B %Y"),
        "month_on_month_change": round(float(mom_change), 1),
        "year_on_year_change": round(float(yoy_change), 1),
        "direction": direction,
        "series_start": cleaned.iloc[0]["period"].strftime("%B %Y"),
        "observations": int(len(cleaned)),
    }


def write_summary_table(summary: dict[str, Any], config: dict[str, Any]) -> str:
    tables_dir = Path(config["paths"]["tables_dir"])
    tables_dir.mkdir(parents=True, exist_ok=True)
    output_path = tables_dir / "headline_summary.csv"
    pd.DataFrame([summary]).to_csv(output_path, index=False)
    return str(output_path)


def write_trend_chart(cleaned: pd.DataFrame, config: dict[str, Any]) -> str:
    figures_dir = Path(config["paths"]["figures_dir"])
    figures_dir.mkdir(parents=True, exist_ok=True)
    output_path = figures_dir / "retail_sales_index_trend.png"

    recent = cleaned.tail(60)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(recent["period"], recent["value"], color="#1f5a85", linewidth=2.4)
    ax.scatter(recent.iloc[-1]["period"], recent.iloc[-1]["value"], color="#c43c39", zorder=5)
    ax.set_title("Retail Sales Index, latest 5 years", loc="left", fontsize=15, fontweight="bold")
    ax.set_ylabel("Index, 2019 = 100")
    ax.set_xlabel("")
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    return str(output_path)
