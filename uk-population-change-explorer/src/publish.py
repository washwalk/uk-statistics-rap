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
        f"<tr><td>{html.escape(row['period'])}</td><td>{html.escape(row['area_name'])}</td><td>{html.escape(row['population'])}</td><td>{html.escape(row['percent_change_from_previous'])}</td></tr>"
        for row in rows[-8:]
    )
    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head><meta charset=\"utf-8\"><title>UK Population Change Explorer</title></head>",
                "<body>",
                "<h1>UK Population Change Explorer</h1>",
                f"<p>Latest {html.escape(latest['measure'])}: <strong>{html.escape(latest['population'])}</strong> for {html.escape(latest['period'])}.</p>",
                "<table><thead><tr><th>Period</th><th>Area</th><th>Population</th><th>Change from previous (%)</th></tr></thead><tbody>",
                table_rows,
                "</tbody></table>",
                "<p>Source: Office for National Statistics, Open Government Licence. Population estimates can be revised as methods and source inputs improve.</p>",
                "</body></html>",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
