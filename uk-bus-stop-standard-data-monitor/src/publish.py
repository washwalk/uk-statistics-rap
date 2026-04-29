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


def fmt_datetime(value: str) -> str:
    if not value:
        return "Not available"
    return value.replace("T", " ").split("+", 1)[0]


def fmt_count_percent(count: int | str, total: int | str, percent: int | float | str) -> str:
    return f"{fmt_count(count)} / {fmt_count(total)} ({fmt_percent(percent)})"


def status_label(status: str) -> str:
    return {"available": "Available", "partial": "Partial", "not_available": "Data gap"}.get(status, status)


def quality_flag_label(flag: str) -> str:
    labels = {
        "all_records_have_street": "All records have Street populated",
        "low_public_stop_code_completeness": "Low public stop code completeness",
        "no_wgs84_coordinates": "No WGS84 longitude/latitude",
    }
    return labels.get(flag, flag.replace("_", " ").capitalize())


def quality_flag_examples(flags: list[dict], flag: str) -> str:
    names = [row.get("area_name") or row.get("area_code") for row in flags if row.get("flag") == flag]
    examples = ", ".join(html.escape(name) for name in names[:3] if name)
    if len(names) > 3:
        examples += f", plus {len(names) - 3} more"
    return examples


def field_missing_count(completeness_rows: list[dict], field: str) -> int:
    for row in completeness_rows:
        if row["field"] == field:
            return int(row["records_missing"])
    raise ValueError(f"Missing completeness row for {field}")


def area_review_notes(row: dict) -> list[str]:
    notes = []
    if float(row["with_coordinates_percent"]) == 0:
        notes.append("WGS84 fields blank; grid references exist")
    elif float(row["with_coordinates_percent"]) < 100:
        notes.append("Some WGS84 coordinates are missing")
    if float(row["with_naptan_code_percent"]) < 95:
        notes.append("Many records lack public stop codes")
    if float(row["with_street_percent"]) < 95:
        notes.append("Many records lack street labels")
    return notes


def publish() -> None:
    config = load_config()
    area_path = Path(config["paths"]["area_summary"])
    completeness_path = Path(config["paths"]["completeness_summary"])
    data_dictionary_path = Path(config["paths"]["data_dictionary"])
    readiness_path = Path(config["paths"]["standard_readiness"])
    audit_requirements_path = Path(config["paths"]["audit_requirements"])
    example_stop_audit_path = Path(config["paths"]["example_stop_audit"])
    metadata_path = Path(config["paths"]["run_metadata"])
    report_path = Path(config["paths"]["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_dir = report_path.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    area_rows = read_csv(area_path)
    completeness_rows = read_csv(completeness_path)
    data_dictionary_rows = read_csv(data_dictionary_path)
    readiness_rows = read_csv(readiness_path)
    audit_requirement_rows = read_csv(audit_requirements_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    total_stops = int(metadata["output_row_counts"]["bus_stop_rows"])
    area_count = int(metadata["quality_counts"]["administrative_areas"])
    status_counts = metadata.get("quality_counts", {}).get("status_counts", {})
    active_stops = int(status_counts.get("active", 0))
    inactive_stops = int(status_counts.get("inactive", 0))
    pending_stops = int(status_counts.get("pending", 0))
    other_status_stops = total_stops - active_stops - inactive_stops - pending_stops
    not_active_stops = total_stops - active_stops
    modification_counts = metadata.get("quality_counts", {}).get("modification_counts", {})
    modification_datetime_summary = metadata.get("quality_counts", {}).get("modification_datetime_summary", {})
    any_location_count = sum(int(row["with_any_location_reference"]) for row in area_rows)
    any_location_percent = (any_location_count / total_stops) * 100
    measurable = sum(1 for row in readiness_rows if row["national_data_status"] in {"available", "partial"})
    data_gap_count = sum(1 for row in readiness_rows if row["national_data_status"] == "not_available")
    run_timestamp = metadata["run_timestamp"].replace("T", " ").split(".", 1)[0]
    missing_public_codes = field_missing_count(completeness_rows, "NaptanCode")
    missing_street = field_missing_count(completeness_rows, "Street")
    missing_longitude = field_missing_count(completeness_rows, "Longitude")
    no_wgs84_area_count = sum(1 for row in area_rows if float(row["with_coordinates_percent"]) == 0)
    low_public_code_area_count = sum(1 for row in area_rows if float(row["with_naptan_code_percent"]) < 95)
    low_street_area_count = sum(1 for row in area_rows if float(row["with_street_percent"]) < 95)

    area_review_rows = [row for row in area_rows if area_review_notes(row)]
    area_review_rows.sort(
        key=lambda row: (
            len(area_review_notes(row)),
            int(row["stop_count"]),
        ),
        reverse=True,
    )
    area_review_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['administrative_area_name'])} ({html.escape(row['administrative_area_code'])})</td>"
        f"<td>{fmt_count(row['stop_count'])}</td>"
        f"<td>{fmt_percent(row['with_coordinates_percent'])}</td>"
        f"<td>{fmt_percent(row['with_naptan_code_percent'])}</td>"
        f"<td>{fmt_percent(row['with_street_percent'])}</td>"
        f"<td>{html.escape('; '.join(area_review_notes(row)))}</td>"
        "</tr>"
        for row in area_review_rows[:12]
    )
    status_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(status.title())}</td>"
        f"<td>{fmt_count(count)}</td>"
        f"<td>{fmt_percent((int(count) / total_stops) * 100)}</td>"
        "</tr>"
        for status, count in sorted(status_counts.items())
    )
    modification_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(modification.title())}</td>"
        f"<td>{fmt_count(count)}</td>"
        f"<td>{fmt_percent((int(count) / total_stops) * 100)}</td>"
        "</tr>"
        for modification, count in sorted(modification_counts.items())
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
    audit_requirements_table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['standard_feature'])}</td>"
        f"<td>{html.escape(row['audit_field'])}</td>"
        f"<td>{html.escape(row['collection_level'])}</td>"
        f"<td>{html.escape(row['why_needed'])}</td>"
        "</tr>"
        for row in audit_requirement_rows
    )
    can_measure_table = "\n".join(
        [
            "<tr><td>Stop identity and join key</td><td><code>ATCOCode</code>, public stop code and stop name are available for national linking and lookup.</td><td>Whether the physical flag is present, legible, branded or showing route destinations.</td></tr>",
            "<tr><td>Location backbone</td><td>WGS84 coordinates or grid references provide a national location baseline for registered records.</td><td>Whether the mapped position is passenger-ready, accessible or recently field checked.</td></tr>",
            "<tr><td>Register status</td><td>NaPTAN marks records as active, inactive or pending and records register modifications.</td><td>Whether a physical stop has been inspected, repaired, cleaned or maintained.</td></tr>",
            "<tr><td>Area-level data quality</td><td>NPTG administrative areas allow local completeness summaries and review prompts.</td><td>Which organisation owns or maintains each stop asset.</td></tr>",
            "<tr><td>Standard readiness</td><td>The monitor can show which proposed standard features have national data evidence.</td><td>Shelter, seating, lighting, printed timetable, route map, RTI display, QR/weblink, cleaning or repair compliance.</td></tr>",
        ]
    )
    facility_source_table = "\n".join(
        [
            "<tr><td>Stop identity</td><td><code>atco_code</code>; <code>audit_date</code></td><td>NaPTAN and local audit records</td><td>Joins local facility evidence to the national stop register.</td></tr>",
            "<tr><td>Shelter and seating</td><td><code>has_shelter</code>; <code>has_seating</code>; <code>shelter_condition_rating</code></td><td>Council asset systems, advertising shelter contracts, maintenance contractors</td><td>Shows whether passengers have basic comfort and weather protection.</td></tr>",
            "<tr><td>Lighting</td><td><code>has_lighting</code>; <code>lighting_working</code>; <code>lighting_ownership</code></td><td>Highways and street-lighting asset systems</td><td>Supports safety, accessibility and personal-security checks.</td></tr>",
            "<tr><td>Passenger information</td><td><code>has_printed_timetable</code>; <code>has_route_map</code>; <code>has_qr_or_weblink</code></td><td>LTA passenger transport teams, operators, print contractors</td><td>Shows whether passengers can understand services at the physical stop.</td></tr>",
            "<tr><td>Real-time information</td><td><code>has_rti_display</code>; <code>rti_display_working</code>; <code>rti_last_checked_datetime</code></td><td>RTI supplier systems, control rooms, LTA transport systems</td><td>Shows whether digital displays exist and are working for passengers.</td></tr>",
            "<tr><td>Maintenance</td><td><code>inspection_frequency</code>; <code>condition_rating</code>; <code>responsible_body</code>; <code>open_defect_status</code></td><td>CRM systems, work-order systems, contractor logs</td><td>Creates accountability for inspections, cleaning and repairs.</td></tr>",
            "<tr><td>Passenger reporting</td><td><code>report_category</code>; <code>report_status</code>; <code>verified_date</code></td><td>Passenger reporting app or web form</td><td>Adds lived-experience evidence for triage, verification and repair follow-up.</td></tr>",
        ]
    )
    quality_flags = metadata.get("quality_counts", {}).get("quality_flags", [])
    quality_flag_counts = {}
    for row in quality_flags:
        quality_flag_counts[row.get("flag", "unknown")] = quality_flag_counts.get(row.get("flag", "unknown"), 0) + 1
    quality_flag_items = "".join(
        f"<li><strong>{html.escape(quality_flag_label(flag))}:</strong> {fmt_count(count)} administrative areas. Examples: {quality_flag_examples(quality_flags, flag)}</li>"
        for flag, count in sorted(quality_flag_counts.items())
    ) or "<li>No quality-review prompts were generated.</li>"

    shutil.copyfile(area_path, data_dir / "area-summary.csv")
    shutil.copyfile(completeness_path, data_dir / "completeness-summary.csv")
    shutil.copyfile(data_dictionary_path, data_dir / "data-dictionary.csv")
    shutil.copyfile(readiness_path, data_dir / "standard-readiness.csv")
    shutil.copyfile(audit_requirements_path, data_dir / "audit-requirements.csv")
    shutil.copyfile(example_stop_audit_path, data_dir / "example-stop-audit.csv")
    shutil.copyfile(metadata_path, data_dir / "run-metadata.json")

    report_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<head>",
                "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
                "<title>UK Bus Stop Standard Data Monitor</title>",
                "<style>body{font-family:Arial,sans-serif;margin:0;color:#1f2933;background:#f5f2eb}header{background:#b02a20;color:white;padding:1rem 1.25rem}header a{color:white}.wrap{max-width:1080px;margin:auto;padding:1.25rem}.hero,.panel,.metric{background:white;border:1px solid #ead9ce;border-radius:16px;padding:1.25rem;margin:1rem 0}.hero{border-top:8px solid #4f4a99}.lede{font-size:1.2rem;color:#4a5568}.metrics,.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}.label{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#6b5b95;font-weight:700}.value{font-size:2rem;font-weight:800;margin:.25rem 0;color:#b02a20}.callout{background:#eef7df;border-left:6px solid #76b947;padding:1rem;border-radius:12px}.warning{background:#fff7ed;border-left:6px solid #f97316;padding:1rem;border-radius:12px}.card{background:#faf7f2;border:1px solid #ead9ce;border-radius:12px;padding:1rem}.card h3{margin-top:0}.talking-points li,.actions li{margin-bottom:.45rem}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid #ead9ce;padding:.65rem;text-align:left;vertical-align:top}th{background:#f3e8ff}.status{display:inline-block;border-radius:999px;padding:.2rem .55rem;font-weight:700}.available{background:#dcfce7;color:#166534}.partial{background:#fef3c7;color:#92400e}.not_available{background:#fee2e2;color:#991b1b}.downloads a{display:inline-block;margin-right:1rem;margin-bottom:.5rem}.download-card a{font-weight:700}@media(max-width:700px){.wrap{padding:.75rem}table{font-size:.9rem;display:block;overflow-x:auto}} </style>",
                "</head>",
                "<body>",
                "<header><a href=\"../\">UK Statistics RAP</a></header>",
                "<main class=\"wrap\">",
                "<section class=\"hero\">",
                "<p class=\"label\">Open data RAP prototype</p>",
                "<h1>UK Bus Stop Standard Data Monitor</h1>",
                "<p class=\"lede\">The UK can already identify and locate registered bus stops nationally. What it cannot yet do from national open data is tell passengers, campaigners or authorities whether each stop has the facilities a National Bus Stop Standard would require.</p>",
                "<div class=\"callout\"><strong>Core finding:</strong> NaPTAN provides a strong stop-register backbone, but the missing layer is published stop-level facility and maintenance data. Missing data does not mean missing facilities; it means the evidence needed for public accountability is not consistently open and joinable.</div>",
                "</section>",
                "<section class=\"metrics\">",
                f"<article class=\"metric\"><p class=\"label\">Register backbone</p><p class=\"value\">{fmt_count(total_stops)}</p><p>Registered NaPTAN records filtered to bus stop infrastructure.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Active records</p><p class=\"value\">{fmt_count(active_stops)}</p><p>{fmt_count(not_active_stops)} filtered records are inactive, pending or another status.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Administrative areas</p><p class=\"value\">{fmt_count(area_count)}</p><p>Area summaries joined to official NPTG administrative area names.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Any location reference</p><p class=\"value\">{fmt_percent(any_location_percent)}</p><p>Records with either WGS84 coordinates or a grid reference.</p></article>",
                f"<article class=\"metric\"><p class=\"label\">Features evidenced</p><p class=\"value\">{measurable} of {len(readiness_rows)}</p><p>{data_gap_count} proposed features need local facility or maintenance evidence.</p></article>",
                "</section>",
                f"<section class=\"panel warning\"><h2>Relationship to Campaign for Better Transport's Report</h2><p>This page does not reproduce <a href=\"https://bettertransport.org.uk/better-bus-stops/\"><em>Better Bus Stops: Creating a national bus stop standard</em></a>. It is a data implementation companion: it tests what a national monitoring pipeline could measure today and identifies the facility fields that local transport authorities would need to audit.</p><p>Data refreshed: {html.escape(run_timestamp)} UTC.</p></section>",
                f"<section class=\"panel callout\"><h2>The Data Story In Five Points</h2><ol class=\"actions\"><li>NaPTAN gives Great Britain a national register backbone for <strong>{fmt_count(total_stops)}</strong> bus stop records.</li><li>The register can support identity, location, status and field-completeness checks across <strong>{fmt_count(area_count)}</strong> administrative areas.</li><li>Current national open data has direct or partial evidence for only <strong>{measurable} of {len(readiness_rows)}</strong> proposed standard features.</li><li>The remaining <strong>{data_gap_count} of {len(readiness_rows)}</strong> features need stop-level facility, condition, inspection or maintenance evidence.</li><li>The practical solution is a national open facilities register joined to NaPTAN using <code>ATCOCode</code>.</li></ol></section>",
                "<section class=\"panel\"><h2>What National Data Can And Cannot Measure</h2><p>The national register is the right foundation for a monitor, but it is not the same thing as facility evidence. The table below separates what the current data can support from what still needs local publication or audit.</p><table><caption>Current national open-data capability and remaining evidence gaps.</caption><thead><tr><th scope=\"col\">Theme</th><th scope=\"col\">Can measure nationally today</th><th scope=\"col\">Cannot prove nationally today</th></tr></thead><tbody>",
                can_measure_table,
                "</tbody></table></section>",
                f"<section class=\"panel callout\"><h2>Campaigning Talking Points</h2><ul class=\"talking-points\"><li>National open data has direct or partial evidence for only <strong>{measurable} of {len(readiness_rows)}</strong> proposed bus stop standard features; <strong>{data_gap_count} of {len(readiness_rows)}</strong> need local stop-level audit evidence.</li><li>The weakest link is not the stop register; it is the absence of a published national facility and maintenance layer.</li><li>NaPTAN can identify registered stops, but it cannot tell passengers whether a stop has a shelter, seat, lighting, printed timetable, route map or working real-time display.</li><li>A national bus stop standard needs a national facility data standard, joined to NaPTAN using <code>ATCOCode</code>.</li><li>If shelters, signs and displays are monitored for contracts or repairs, passengers should be able to see stop-level status as open data.</li><li>Missing data is not the same as missing facilities, but it does limit public accountability.</li></ul></section>",
                "<section class=\"panel\"><h2>What This Means For Campaigners</h2><p>Use this page to argue for better stop-level evidence, not to claim that individual stops pass or fail a standard. Current national open data can locate registered bus stops and check some basic information fields, but it cannot prove whether the facilities passengers rely on are present, maintained or working.</p><p>Where authorities already hold shelter, lighting, real-time information or maintenance data, the campaign ask is publication and standardisation. Where they do not hold it, the ask is a stop-level audit.</p><div class=\"cards actions\"><article class=\"card\"><h3>Ask your LTA</h3><ul><li>Which stop-level facility data do you already hold?</li><li>Can each record be joined to NaPTAN using <code>ATCOCode</code>?</li><li>Who owns or maintains each shelter, sign, display, lighting asset and timetable case?</li><li>When was each facility last checked, and is there an open defect status?</li><li>Will the data be published under an open licence and updated regularly?</li></ul></article><article class=\"card\"><h3>Use the downloads</h3><ul><li>Find gaps in your area using the area summary.</li><li>Ask the right evidence questions using the audit requirements.</li><li>Start collecting stop-level evidence with the example audit template.</li></ul></article></div></section>",
                "<section class=\"panel\"><h2>The Missing Link: Published Stop-Level Facility Data</h2><p>In many areas, some facility data probably already exists in local authority, highway, contractor, shelter, lighting or real-time information systems. The problem is that it is not consistently published as open, stop-level data that passengers, campaigners and researchers can join to NaPTAN.</p><p>Current national open data can identify registered bus stops, but it cannot show, for each stop, whether shelters, seats, lighting, timetable cases, route maps, QR codes or real-time displays exist, work, are inspected, or have a named maintenance owner.</p><p><strong>Where the data exists, publish it. Where it does not, audit it. In both cases, link it to NaPTAN <code>ATCOCode</code> and keep it updated.</strong></p></section>",
                "<section class=\"panel\"><h2>Where The Data May Already Sit</h2><div class=\"cards\"><article class=\"card\"><h3>Shelters and seating</h3><p>Council asset systems, advertising shelter contracts and maintenance contractors may hold shelter ownership, condition and repair records.</p></article><article class=\"card\"><h3>Lighting</h3><p>Highways and street-lighting teams may hold lighting assets, ownership and fault status, often outside transport teams.</p></article><article class=\"card\"><h3>Real-time displays</h3><p>RTI suppliers, control rooms and LTA transport systems may monitor device presence and uptime internally.</p></article><article class=\"card\"><h3>Timetables, flags and maps</h3><p>Passenger transport teams, operators and print contractors may manage stop flags, printed timetable cases, route maps and updates.</p></article><article class=\"card\"><h3>Cleaning and repairs</h3><p>CRM systems, work-order systems and contractor logs may record inspections, defects, cleaning and repairs.</p></article><article class=\"card\"><h3>Passenger reports</h3><p>Council reporting tools, operator complaints and FixMyStreet-style services may contain useful issue evidence, but not in a common stop-level schema.</p></article></div></section>",
                "<section class=\"panel\"><h2>What To Demand</h2><ul class=\"actions\"><li>Ask for the dataset, not only the policy commitment.</li><li>Publish stop-level facility data as open data using NaPTAN <code>ATCOCode</code> as the common stop identifier.</li><li>Name the responsible body and asset owner for each relevant facility.</li><li>Publish whether each facility exists, whether it is working, and when it was last checked.</li><li>Include repair, cleaning, inspection, condition and open defect status.</li><li>Publish updates on a regular schedule under an open licence.</li><li>Provide a passenger reporting route for missing, damaged or unsafe stop facilities, with public follow-up statuses.</li></ul></section>",
                "<section class=\"panel\"><h2>The Data-Based Solution: A National Bus Stop Facilities Register</h2><p>A practical solution would be a national open bus stop facilities register. NaPTAN would remain the national stop ID and location backbone. Local transport authorities and asset owners would publish facility and maintenance records linked to <code>ATCOCode</code>. Passenger reports could be used as a feedback loop, with reports verified by the responsible authority before being marked as fixed or unresolved.</p><p>A minimum viable register would have one stop-level row per audit or asset record, with fields for facility presence, working status, condition, last checked date, responsible body, asset owner, evidence URL and open defect status.</p><div class=\"callout\"><strong>Data flow:</strong> NaPTAN stop register + LTA facility records + asset maintenance records + passenger reports -> national facilities register -> public dashboard and compliance monitor.</div><table><caption>Proposed evidence model for a national bus stop facilities register.</caption><thead><tr><th scope=\"col\">Need</th><th scope=\"col\">Example fields</th><th scope=\"col\">Likely source</th><th scope=\"col\">Why it matters</th></tr></thead><tbody>",
                facility_source_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Passenger Reporting Feedback Loop</h2><p>A national reporting tool could let passengers submit stop-level evidence such as photos, GPS location, issue category and free-text notes. Reports should be linked to <code>ATCOCode</code> where possible, assigned to a responsible body, verified, and tracked through statuses such as reported, verified, referred, fixed or unresolved.</p><p>Passenger reports should support official audits, not replace them. A report is evidence of a potential issue until the responsible authority verifies it.</p></section>",
                f"<section class=\"panel\"><h2>Current Register Status</h2><p>The monitor keeps all registered NaPTAN bus stop records in scope for transparency, but the register also marks records by status. Of the {fmt_count(total_stops)} filtered bus stop records, {fmt_count(active_stops)} are marked active, {fmt_count(inactive_stops)} inactive, {fmt_count(pending_stops)} pending, and {fmt_count(other_status_stops)} have another or blank status.</p><p><strong>Important caveat:</strong> NaPTAN <code>Status</code> and <code>ModificationDateTime</code> describe the register record. They are not evidence that a physical stop has recently been inspected, maintained, repaired, or checked for passenger facilities.</p><div class=\"cards\"><article class=\"card\"><h3>Status breakdown</h3><table><thead><tr><th scope=\"col\">Status</th><th scope=\"col\">Records</th><th scope=\"col\">Share</th></tr></thead><tbody>{status_table}</tbody></table></article><article class=\"card\"><h3>Record modification</h3><p>{fmt_count(modification_datetime_summary.get('records_with_modification_datetime', 0))} records have a modification timestamp and {fmt_count(modification_datetime_summary.get('records_missing_modification_datetime', 0))} do not.</p><p>Earliest timestamp: {html.escape(fmt_datetime(modification_datetime_summary.get('earliest_modification_datetime', '')))}.<br>Latest timestamp: {html.escape(fmt_datetime(modification_datetime_summary.get('latest_modification_datetime', '')))}.</p><table><thead><tr><th scope=\"col\">Modification</th><th scope=\"col\">Records</th><th scope=\"col\">Share</th></tr></thead><tbody>{modification_table}</tbody></table></article></div></section>",
                "<section class=\"panel warning\"><h2>How to Read the Percentages</h2><p>Percentages on this page are NaPTAN field-completeness rates for registered bus stop records. They do not measure bus route coverage, street coverage, passenger facilities, or compliance with a bus stop standard.</p><p><code>Street</code> means the stop record has a street label. It does not mean that share of streets has a bus route. <code>Longitude/latitude</code> means WGS84 coordinate fields are populated; 0% means those fields are blank in NaPTAN for that area, not necessarily that no location reference exists anywhere.</p></section>",
                f"<section class=\"panel\"><h2>Where Existing Stop Data Needs Attention</h2><p>These are not compliance failures. They show where the national stop register may be harder to use for public-facing accountability, mapping or passenger information checks. Across all areas, <strong>{fmt_count(missing_public_codes)}</strong> records are missing a public stop code, <strong>{fmt_count(missing_street)}</strong> are missing a street label, and <strong>{fmt_count(missing_longitude)}</strong> are missing WGS84 longitude/latitude.</p><div class=\"cards\"><article class=\"card\"><p class=\"label\">No WGS84 longitude/latitude</p><p class=\"value\">{fmt_count(no_wgs84_area_count)}</p><p>Administrative areas where WGS84 fields are blank for all filtered bus stop records.</p></article><article class=\"card\"><p class=\"label\">Public stop code below 95%</p><p class=\"value\">{fmt_count(low_public_code_area_count)}</p><p>Administrative areas where public-facing stop-code completeness is below 95%.</p></article><article class=\"card\"><p class=\"label\">Street below 95%</p><p class=\"value\">{fmt_count(low_street_area_count)}</p><p>Administrative areas where street-label completeness is below 95%.</p></article></div><p>Full area-level counts for all {fmt_count(area_count)} administrative areas are available in the area-summary download.</p><table><caption>Selected administrative areas with notable NaPTAN field-completeness issues.</caption><thead><tr><th scope=\"col\">Administrative area</th><th scope=\"col\">Stops</th><th scope=\"col\">WGS84</th><th scope=\"col\">Public stop code</th><th scope=\"col\">Street</th><th scope=\"col\">Why review</th></tr></thead><tbody>",
                area_review_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Other Data-Quality Review Prompts</h2><p>These prompts support follow-up questions about the source data. They are not judgements on local authority performance and they do not prove that facilities are present or absent.</p><ul>",
                quality_flag_items,
                "</ul></section>",
                "<section class=\"panel\"><h2>NaPTAN Field Completeness</h2><table><caption>National field-completeness rates for filtered bus stop records.</caption><thead><tr><th scope=\"col\">Field</th><th scope=\"col\">Present</th><th scope=\"col\">Missing records</th><th scope=\"col\">Why it matters</th></tr></thead><tbody>",
                completeness_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Data Dictionary</h2><p>This table defines how the monitor interprets key fields and, just as importantly, what each field does not prove.</p><table><caption>Definitions and caveats for key NaPTAN/NPTG fields used by the monitor.</caption><thead><tr><th scope=\"col\">Field</th><th scope=\"col\">Monitor interpretation</th><th scope=\"col\">Does not prove</th></tr></thead><tbody>",
                data_dictionary_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Standard Readiness</h2><p><strong>Data gap</strong> means the feature is not available in current national open data. It does not mean the facility is absent at the stop.</p><table><caption>Readiness of national open data to monitor proposed bus stop standard features.</caption><thead><tr><th scope=\"col\">Proposed standard feature</th><th scope=\"col\">CBT category requirement</th><th scope=\"col\">National data status</th><th scope=\"col\">Monitoring note</th></tr></thead><tbody>",
                readiness_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>What LTAs Would Need To Collect Or Publish</h2><p>A compliance monitor would need stop-level audit evidence joined to NaPTAN using <code>ATCOCode</code>. Some of this data may already exist in local authority, asset-owner or contractor systems. The fields below are an implementation checklist, not a statement that the facilities are absent.</p><table><caption>Stop-level audit fields needed to fill national open-data gaps.</caption><thead><tr><th scope=\"col\">Proposed standard feature</th><th scope=\"col\">Audit fields</th><th scope=\"col\">Collection level</th><th scope=\"col\">Why needed</th></tr></thead><tbody>",
                audit_requirements_table,
                "</tbody></table></section>",
                "<section class=\"panel\"><h2>Method</h2><p>The pipeline fetches the NaPTAN national access-node CSV and the NPTG gazetteer XML, filters bus stop records, joins official administrative area names, produces area and completeness summaries, and publishes a standard-readiness matrix based on Campaign for Better Transport's proposed categories and features.</p><p>Offline tests validate transformation logic and committed outputs. Live NaPTAN and NPTG refresh checks are kept in <code>make integration-test</code>.</p></section>",
                "<section class=\"panel\"><h2>Assurance and Downloads</h2>",
                "<p>Downloads support five practical jobs: find gaps, ask the right questions, collect evidence, check caveats and reproduce the analysis.</p><div class=\"cards\"><article class=\"card download-card\"><h3>Find gaps in your area</h3><p><a href=\"data/area-summary.csv\">Area summary CSV</a></p><p>Stop counts and completeness rates for every administrative area.</p></article><article class=\"card download-card\"><h3>Ask the right questions</h3><p><a href=\"data/audit-requirements.csv\">Audit requirements CSV</a></p><p>Fields needed to evidence shelter, seating, lighting, information and maintenance provision.</p></article><article class=\"card download-card\"><h3>Start collecting evidence</h3><p><a href=\"data/example-stop-audit.csv\">Example stop-audit template</a></p><p>Illustrative stop-level template keyed by <code>atco_code</code>.</p></article><article class=\"card download-card\"><h3>Check what data proves</h3><p><a href=\"data/data-dictionary.csv\">Data dictionary CSV</a></p><p>Definitions of what each NaPTAN/NPTG field does and does not prove.</p></article></div><p class=\"downloads\"><a href=\"data/completeness-summary.csv\">Download completeness summary</a><a href=\"data/standard-readiness.csv\">Download standard readiness matrix</a><a href=\"data/run-metadata.json\">Download run metadata</a><a href=\"https://github.com/washwalk/uk-statistics-rap/blob/main/uk-bus-stop-standard-data-monitor/methodology.md\">Read methodology</a></p></section>",
                "<section class=\"panel\"><h2>Limitations</h2><p>NaPTAN covers England, Scotland and Wales and is a national transport reference dataset rather than an official statistics release. It does not include Northern Ireland and does not consistently record passenger facility provision such as shelter, seating, printed timetables, route maps, lighting, or real-time displays.</p>",
                f"<p>Sources: <a href=\"{html.escape(config['source']['url'])}\">{html.escape(config['source']['publisher'])} NaPTAN API</a> and <a href=\"{html.escape(config['source']['nptg_url'])}\">{html.escape(config['source']['publisher'])} NPTG API</a>, Open Government Licence.</p></section>",
                "</main>",
                "</body></html>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    publish()
