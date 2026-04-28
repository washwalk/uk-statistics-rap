from __future__ import annotations

import csv
import html
import json
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def publish() -> None:
    config = load_config()
    processed_path = Path(config["paths"]["processed_data"])
    report_path = Path(config["paths"]["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    latest = rows[-1]
    table_rows = "\n".join(
        f"<tr><td>{html.escape(row['period'])}</td><td>{html.escape(row['value'])}</td><td>{html.escape(row['change_from_previous'])}</td></tr>"
        for row in rows[-12:]
    )
    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>UK Inflation Monitor</title></head>",
                "<body>",
                "<p><a href=\"../\">Back to UK Statistics RAP</a></p>",
                "<h1>UK Inflation Monitor</h1>",
                f"<p>Latest {html.escape(latest['measure'])}: <strong>{html.escape(latest['value'])}</strong> for {html.escape(latest['period'])}.</p>",
                "<h2>Method</h2>",
                "<p>The pipeline fetches one ONS CPIH time series, keeps valid numeric observations, and calculates the absolute change from the previous period.</p>",
                "<h2>Recent Observations</h2>",
                "<table><thead><tr><th>Period</th><th>Value</th><th>Change from previous</th></tr></thead><tbody>",
                table_rows,
                "</tbody></table>",
                "<h2>Limitations</h2>",
                "<p>This compact example uses a single headline time series and does not replace a full inflation statistical bulletin. Values may be revised by ONS.</p>",
                "<p>Source: Office for National Statistics, Open Government Licence.</p>",
                "</body></html>",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
