from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fmt_count(value: int | str) -> str:
    return f"{int(value):,}"


def fmt_percent(value: int | float | str) -> str:
    return f"{float(value):.1f}%"


def fmt_count_percent(count: int | str, total: int | str, percent: int | float | str) -> str:
    return f"{fmt_count(count)} / {fmt_count(total)} ({fmt_percent(percent)})"


def status_label(status: str) -> str:
    return {"available": "Available", "partial": "Partial", "not_available": "Data gap"}.get(status, status)


def publish() -> None:
    config = load_config()
    area_path = Path(config["paths"]["area_summary"])
    completeness_path = Path(config["paths"]["completeness_summary"])
    data_dictionary_path = Path(config["paths"]["data_dictionary"])
    readiness_path = Path(config["paths"]["standard_readiness"])
    metadata_path = Path(config["paths"]["run_metadata"])
    report_path = Path(config["paths"]["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_dir = report_path.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    area_rows = read_csv(area_path)
    completeness_rows = read_csv(completeness_path)
    data_dictionary_rows = read_csv(data_dictionary_path)
    readiness_rows = read_csv(readiness_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    total_stops = int(metadata["output_row_counts"]["bus_stop_rows"])
    area_count = int(metadata["quality_counts"]["administrative_areas"])
    coordinate_row = next(row for row in completeness_rows if row["field"] == "Longitude")
    naptan_row = next(row for row in completeness_rows if row["field"] == "NaptanCode")
    measurable = sum(1 for row in readiness_rows if row["national_data_status"] in {"available", "partial"})
    readiness_percent = (measurable / len(readiness_rows)) * 100

    top_area_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['administrative_area_name'])} ({html.escape(row['administrative_area_code'])})</td>"
        f"<td>{fmt_count(row['stop_count'])}</td>"
        f"<td>{fmt_count_percent(row['with_coordinates'], row['stop_count'], row['with_coordinates_percent'])}</td>"
        f"<td>{fmt_count_percent(row['with_grid_reference'], row['stop_count'], row['with_grid_reference_percent'])}</td>"
        f"<td>{fmt_count_percent(row['with_any_location_reference'], row['stop_count'], row['with_any_location_reference_percent'])}</td>"
        f"<td>{fmt_count_percent(row['with_naptan_code'], row['stop_count'], row['with_naptan_code_percent'])}</td>"
        f"<td>{fmt_count_percent(row['with_street'], row['stop_count'], row['with_street_percent'])}</td>"
        "</tr>"
        for row in area_rows[:15]
    )
    completeness_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['field'])}</td>"
        f"<td>{fmt_percent(row['percent_present'])}</td>"
        f"<td>{fmt_count(row['records_missing'])}</td>"
        f"<td>{html.escape(row['why_it_matters'])}</td>"
        "</tr>"
        for row in completeness_rows
    )
    data_dictionary_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['field'])}</td>"
        f"<td>{html.escape(row['monitor_interpretation'])}</td>"
        f"<td>{html.escape(row['does_not_prove'])}</td>"
        "</tr>"
        for row in data_dictionary_rows
    )
    readiness_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['standard_feature'])}</td>"
        f"<td>{html.escape(row['cbt_category_requirement'])}</td>"
        f"<td><span class=\"status {html.escape(row['national_data_status'])}\">{html.escape(status_label(row['national_data_status']))}</span></td>"
        f"<td>{html.escape(row['monitoring_note'])}</td>"
        "</tr>"
        for row in readiness_rows
    )
    quality_flags = metadata.get("quality_counts", {}).get("quality_flags", [])
    quality_flag_counts = {}
    for row in quality_flags:
        quality_flag_counts[row.get("flag", "unknown")] = quality_flag_counts.get(row.get("flag", "unknown"), 0) + 1
    quality_flag_items = "".join(
        f"<li><strong>{html.escape(flag.replace('_', ' '))}:</strong> {fmt_count(count)} administrative areas</li>"
        for flag, count in sorted(quality_flag_counts.items())
    ) or "<li>No quality-review prompts were generated.</li>"

    shutil.copyfile(area_path, data_dir / "area-summary.csv")
    shutil.copyfile(completeness_path, data_dir / "completeness-summary.csv")
    shutil.copyfile(data_dictionary_path, data_dir / "data-dictionary.csv")
    shutil.copyfile(readiness_path, data_dir / "standard-readiness.csv")
    shutil.copyfile(metadata_path, data_dir / "run-metadata.json")

    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head>",
                "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
                "<title>UK Bus Stop Standard Data Monitor</title>",
                "<style>body{font-family:Arial,sans-serif;margin:0;color:#1f2933;background:#f5f2eb}header{background:#b02a20;color:white;padding:1rem 1.25rem}header a{color:white}.wrap{max-width:1080px;margin:auto;padding:1.25rem}.hero,.panel,.metric{background:white;border:1px solid #ead9ce;border-radius:16px;padding:1.25rem;margin:1rem 0}.hero{border-top:8px solid #4f4a99}.lede{font-size:1.2rem;color:#4a5568}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}.label{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#6b5b95;font-weight:700}.value{font-size:2rem;font-weight:800;margin:.25rem 0;color:#b02a20}.callout{background:#eef7df;border-left:6px solid #76b947;padding:1rem;border-radius:12px}.warning{background:#fff7ed;border-left:6px solid #f97316;padding:1rem;border-radius:12px}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid #ead9ce;padding:.65rem;text-align:left;vertical-align:top}th{background:#f3e8ff}.status{display:inline-block;border-radius:999px;padding:.2rem .55rem;font-weight:700}.available{background:#dcfce7;color:#166534}.partial{background:#fef3c7;color:#92400e}.not_available{background:#fee2e2;color:#991b1b}.downloads a{display:inline-block;margin-right:1rem;margin-bottom:.5rem}@media(max-width:700px){.wrap{padding:.75rem}table{font-size:.9rem;display:block;overflow-x:auto}} </style>",
                "</head>",
                "<body>",
                "<header><a href=\"../\">UK Statistics RAP</a></header>",
                "<main class=\"wrap\">",
                "<section class=\"hero\">",
                "<p class=\"label\">Open data RAP prototype</p>",
                "<h1>UK Bus Stop Standard Data Monitor</h1>",
                "<p class=\"lede\">A reproducible NaPTAN-based prototype showing what national open data can currently tell us about the bus stop estate, and what extra facility data would be needed to monitor a National Bus Stop Standard.</p>",
                "<div class=\"callout\"><strong>Core finding:</strong> national open data can provide a stop register and data-quality baseline, but it cannot confirm whether each stop meets facility standards for shelter, seating, printed timetable information, route maps, lighting, or working real-time displays.</div>",
                "</section>",
                "<section class=\"metrics\">",
                f"<article class=\"metric\"><p class=\"label\">Registered bus stop records</p><p class=\"value\">{fmt_count(total_stops)}</p><p>NaPTAN records filtered to bus stop infrastructure.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Administrative areas</p><p class=\"value\">{fmt_count(area_count)}</p><p>Area summaries joined to official NPTG administrative area names.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Longitude populated</p><p class=\"value\">{fmt_percent(coordinate_row['percent_present'])}</p><p>Coordinate completeness for mapped monitoring.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Available or partially evidenced</p><p class=\"value\">{fmt_percent(readiness_percent)}</p><p>Proposed features with direct or partial evidence in current national open data.</p></article>",
                "</section>",
                "<section class=\"panel warning\"><h2>Relationship to Campaign for Better Transport's Report</h2><p>This page does not reproduce <em>Better Bus Stops: Creating a national bus stop standard</em>. It is a data implementation companion: it tests what a national monitoring pipeline could measure today and identifies the facility fields that local transport authorities would need to audit.</p></section>",
                "<section class=\"panel warning\"><h2>How to Read the Percentages</h2><p>Percentages on this page are NaPTAN field-completeness rates for registered bus stop records. They do not measure bus route coverage, street coverage, passenger facilities, or compliance with a bus stop standard.</p><p><code>Street</code> means the stop record has a street label. It does not mean that share of streets has a bus route. <code>Longitude/latitude</code> means WGS84 coordinate fields are populated; 0% means those fields are blank in NaPTAN for that area, not necessarily that no location reference exists anywhere.</p></section>",
                "<section class=\"panel\"><h2>Largest Areas: NaPTAN Field Completeness</h2><p>Area names are sourced from the DfT National Public Transport Gazetteer and joined to NaPTAN stops using <code>AdministrativeAreaCode</code>. Cells show populated records / total records and the corresponding percentage.</p><table><thead><tr><th>Administrative area</th><th>Stops</th><th>Longitude/latitude populated</th><th>Grid reference populated</th><th>Any location reference</th><th>Public stop code populated</th><th>Street field populated</th></tr></thead><tbody>",
                top_area_rows,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Data-Quality Review Prompts</h2><p>These are prompts for follow-up review, not validation failures. They highlight patterns that can otherwise be misread, such as areas with no WGS84 longitude/latitude or areas where every record has a street label.</p><ul>",
                quality_flag_items,
                "</ul></section>",
                "<section class=\"panel\"><h2>NaPTAN Field Completeness</h2><table><thead><tr><th>Field</th><th>Present</th><th>Missing records</th><th>Why it matters</th></tr></thead><tbody>",
                completeness_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Data Dictionary</h2><p>This table defines how the monitor interprets key fields and, just as importantly, what each field does not prove.</p><table><thead><tr><th>Field</th><th>Monitor interpretation</th><th>Does not prove</th></tr></thead><tbody>",
                data_dictionary_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Standard Readiness</h2><table><thead><tr><th>Proposed standard feature</th><th>CBT category requirement</th><th>National data status</th><th>Monitoring note</th></tr></thead><tbody>",
                readiness_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Method</h2><p>The pipeline fetches the NaPTAN national access-node CSV and the NPTG gazetteer XML, filters bus stop records, joins official administrative area names, produces area and completeness summaries, and publishes a standard-readiness matrix based on Campaign for Better Transport's proposed categories and features.</p><p>Offline tests validate transformation logic and committed outputs. Live NaPTAN and NPTG refresh checks are kept in <code>make integration-test</code>.</p></section>",
                "<section class=\"panel\"><h2>Assurance and Downloads</h2>",
                "<p class=\"downloads\"><a href=\"data/area-summary.csv\">Download area summary</a><a href=\"data/completeness-summary.csv\">Download completeness summary</a><a href=\"data/data-dictionary.csv\">Download data dictionary</a><a href=\"data/standard-readiness.csv\">Download standard readiness matrix</a><a href=\"data/run-metadata.json\">Download run metadata</a><a href=\"https://github.com/washwalk/uk-statistics-rap/blob/main/uk-bus-stop-standard-data-monitor/methodology.md\">Read methodology</a></p></section>",
                "<section class=\"panel\"><h2>Limitations</h2><p>NaPTAN covers England, Scotland and Wales and is a national transport reference dataset rather than an official statistics release. It does not include Northern Ireland and does not consistently record passenger facility provision such as shelter, seating, printed timetables, route maps, lighting, or real-time displays.</p>",
                f"<p>Source: <a href=\"{html.escape(config['source']['url'])}\">{html.escape(config['source']['publisher'])} NaPTAN API</a>, Open Government Licence.</p></section>",
                "</main>",
                "</body></html>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
