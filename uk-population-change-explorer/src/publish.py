from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def fmt_count(value: str) -> str:
    return f"{int(value):,}"


def fmt_change(value: str) -> str:
    if not value:
        return "not available"
    change = int(value)
    sign = "+" if change > 0 else ""
    return f"{sign}{change:,}"


def fmt_percent(value: str) -> str:
    if not value:
        return "not available"
    percent = float(value)
    sign = "+" if percent > 0 else ""
    return f"{sign}{percent:.3f}%"


def publish() -> None:
    config = load_config()
    processed_path = Path(config["paths"]["processed_data"])
    metadata_path = Path(config["paths"]["run_metadata"])
    report_path = Path(config["paths"]["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_dir = report_path.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with processed_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    latest = rows[-1]
    previous = rows[-2] if len(rows) > 1 else None
    table_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['period'])}</td>"
        f"<td>{html.escape(row['area_name'])}</td>"
        f"<td>{fmt_count(row['population'])}</td>"
        f"<td>{html.escape(fmt_change(row['change_from_previous']))}</td>"
        f"<td>{html.escape(fmt_percent(row['percent_change_from_previous']))}</td>"
        "</tr>"
        for row in rows[-8:]
    )
    shutil.copyfile(processed_path, data_dir / "analysis.csv")
    shutil.copyfile(metadata_path, data_dir / "run-metadata.json")
    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head>",
                "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
                "<title>UK Population Change Explorer</title>",
                "<style>body{font-family:Arial,sans-serif;margin:0;color:#172033;background:#f4f8f6}header{background:#164e63;color:white;padding:1rem 1.25rem}header a{color:white}.wrap{max-width:980px;margin:auto;padding:1.25rem}.hero,.panel,.metric{background:white;border:1px solid #d5e6df;border-radius:14px;padding:1.25rem;margin:1rem 0}.lede{font-size:1.2rem;color:#405a52}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.label{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:#55706a}.value{font-size:2rem;font-weight:700;margin:.25rem 0}.change{font-weight:700;color:#0f766e}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid #dcebe5;padding:.65rem;text-align:left}th{background:#e7f3ee}.downloads a{display:inline-block;margin-right:1rem}@media(max-width:640px){.wrap{padding:.75rem}table{font-size:.9rem}} </style>",
                "</head>",
                "<body>",
                "<header><a href=\"../\">UK Statistics RAP</a></header>",
                "<main class=\"wrap\">",
                "<section class=\"hero\">",
                "<p class=\"label\">Official statistics RAP example</p>",
                "<h1>UK Population Change Explorer</h1>",
                "<p class=\"lede\">UK population estimate summary with reproducible source capture, area-period transformation, validation, metadata, and static publication.</p>",
                "</section>",
                "<section class=\"metrics\">",
                f"<article class=\"metric\"><p class=\"label\">Latest period</p><p class=\"value\">{html.escape(latest['period'])}</p><p>{html.escape(latest['area_name'])}</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Latest estimate</p><p class=\"value\">{fmt_count(latest['population'])}</p><p>{html.escape(latest['measure'])}</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Change from previous</p><p class=\"value\">{html.escape(fmt_change(latest['change_from_previous']))}</p><p>{html.escape(fmt_percent(latest['percent_change_from_previous']))}; previous period: {html.escape(previous['period']) if previous else 'not available'}</p></article>",
                "</section>",
                "<section class=\"panel\"><h2>Method</h2>",
                "<p>The pipeline fetches one ONS UK population time series, standardises it to an area-period table, and calculates absolute and percentage change from the previous annual observation.</p>",
                "<p>Offline tests validate transformation logic and committed outputs. Live ONS refresh checks are kept in <code>make integration-test</code>.</p></section>",
                "<section class=\"panel\"><h2>Recent Observations</h2>",
                "<table><thead><tr><th>Period</th><th>Area</th><th>Population</th><th>Change</th><th>Change (%)</th></tr></thead><tbody>",
                table_rows,
                "</tbody></table>",
                "</section>",
                "<section class=\"panel\"><h2>Assurance and Downloads</h2>",
                "<p class=\"downloads\"><a href=\"data/analysis.csv\">Download processed CSV</a><a href=\"data/run-metadata.json\">Download run metadata</a><a href=\"https://github.com/washwalk/uk-statistics-rap/blob/main/uk-population-change-explorer/methodology.md\">Read methodology</a></p>",
                "</section>",
                "<section class=\"panel\"><h2>Limitations</h2>",
                "<p>This compact example uses one UK-level series and does not include subnational breakdowns. Population estimates can be revised as methods and source inputs improve.</p>",
                f"<p>Source: <a href=\"{html.escape(config['source']['url'])}\">Office for National Statistics</a>, Open Government Licence.</p></section>",
                "</main>",
                "</body></html>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
