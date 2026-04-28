from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


def load_config() -> dict:
    return yaml.safe_load(Path("config.yml").read_text(encoding="utf-8"))


def publish() -> None:
    config = load_config()
    processed_path = Path(config["paths"]["processed_data"])
    summary_path = Path(config["paths"]["summary_table"])
    report_path = Path(config["paths"]["report"])
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(processed_path)
    summary = frame.groupby("measure", as_index=False)["value"].agg(["count", "min", "max", "mean"])
    summary.to_csv(summary_path, index=False)

    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head><meta charset=\"utf-8\"><title>Example RAP Output</title></head>",
                "<body>",
                "<h1>Example RAP Output</h1>",
                "<p>Replace this placeholder with your publication output.</p>",
                summary.to_html(index=False),
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
