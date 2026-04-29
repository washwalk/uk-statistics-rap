from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import iterparse


AREA_FIELDS = [
    "administrative_area_code",
    "administrative_area_name",
    "stop_count",
    "with_coordinates",
    "with_coordinates_percent",
    "with_naptan_code",
    "with_naptan_code_percent",
    "with_street",
    "with_street_percent",
    "with_indicator",
    "with_indicator_percent",
    "with_bearing",
    "with_bearing_percent",
    "with_locality",
    "with_locality_percent",
]

COMPLETENESS_FIELDS = ["field", "records_present", "records_missing", "percent_present", "why_it_matters"]
READINESS_FIELDS = ["standard_feature", "cbt_category_requirement", "national_data_status", "available_fields", "monitoring_note"]

COMPLETENESS_NOTES = {
    "ATCOCode": "Unique stop identifier used to link stop records across systems.",
    "NaptanCode": "Public-facing stop code suitable for signs, SMS, apps, and passenger information.",
    "CommonName": "Passenger-facing stop name.",
    "Street": "Street context helps passengers find and distinguish stops.",
    "Indicator": "Short qualifier such as opposite, outside, bay, or stop number.",
    "Bearing": "Direction of travel at the stop.",
    "LocalityName": "Local place name used to group and present stops.",
    "Longitude": "Coordinate needed for mapping and spatial accessibility checks.",
    "Latitude": "Coordinate needed for mapping and spatial accessibility checks.",
    "BusStopType": "Classifies the physical bus stop type where supplied.",
    "TimingStatus": "Indicates timing-point status used in bus service information.",
}

STANDARD_READINESS = [
    {
        "standard_feature": "Bus stop identity and location",
        "cbt_category_requirement": "All categories",
        "national_data_status": "available",
        "available_fields": "ATCOCode; NaptanCode; CommonName; Longitude; Latitude; AdministrativeAreaCode",
        "monitoring_note": "NaPTAN can provide a national stop register and location baseline.",
    },
    {
        "standard_feature": "Bus stop flag with stop name, route numbers, destination and branding",
        "cbt_category_requirement": "Categories 1 to 4",
        "national_data_status": "partial",
        "available_fields": "CommonName; Indicator; Bearing; NaptanCode",
        "monitoring_note": "NaPTAN records stop names and public codes but not whether the physical flag displays routes, destinations, or branding.",
    },
    {
        "standard_feature": "Printed timetable of arrival times",
        "cbt_category_requirement": "Categories 1 to 4",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN does not record whether an up-to-date printed timetable is displayed at the stop.",
    },
    {
        "standard_feature": "Covered shelter with seating",
        "cbt_category_requirement": "Categories 1 to 3",
        "national_data_status": "not_available",
        "available_fields": "BusStopType may describe broad stop form only where populated",
        "monitoring_note": "National open data does not consistently record shelter or seating provision.",
    },
    {
        "standard_feature": "Map of local bus stops and route network",
        "cbt_category_requirement": "Categories 1 to 3",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN does not record whether route maps are displayed at stops.",
    },
    {
        "standard_feature": "Real-time next bus information display",
        "cbt_category_requirement": "Categories 1 to 3",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN does not record whether a working real-time information display is present.",
    },
    {
        "standard_feature": "QR code or weblink to online real-time passenger information",
        "cbt_category_requirement": "Categories 1 to 4",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN does not consistently record physical QR-code or weblink provision at stops.",
    },
    {
        "standard_feature": "Lighting at bus stop",
        "cbt_category_requirement": "Categories 1 to 4",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN does not record whether stops have lighting or whether lighting is working.",
    },
    {
        "standard_feature": "Cleaning, inspection, repair and maintenance arrangements",
        "cbt_category_requirement": "Categories 1 to 4",
        "national_data_status": "not_available",
        "available_fields": "",
        "monitoring_note": "NaPTAN is a stop register and does not hold asset-management contracts or inspection records.",
    },
]


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def is_present(value: str | None) -> bool:
    return bool((value or "").strip())


def is_bus_stop(row: dict) -> bool:
    stop_type = (row.get("StopType") or "").strip().upper()
    bus_stop_type = (row.get("BusStopType") or "").strip().upper()
    return stop_type.startswith("BC") or bool(bus_stop_type)


def has_coordinates(row: dict) -> bool:
    return is_present(row.get("Longitude")) and is_present(row.get("Latitude"))


def percent(part: int, total: int) -> str:
    if total == 0:
        return "0.0"
    return f"{(part / total) * 100:.1f}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_area_names(path: Path) -> dict[str, str]:
    area_names: dict[str, str] = {}
    for event, elem in iterparse(path, events=("end",)):
        if local_name(elem.tag) != "AdministrativeArea":
            continue
        values = {local_name(child.tag): (child.text or "").strip() for child in list(elem)}
        area_code = values.get("AdministrativeAreaCode", "")
        area_name = values.get("Name", "")
        if area_code and area_name:
            area_names[area_code] = area_name
        elem.clear()
    if not area_names:
        raise ValueError("No administrative area names were available in NPTG data")
    return area_names


def build_outputs(rows: list[dict], area_names: dict[str, str] | None = None) -> tuple[list[dict], list[dict], list[dict], dict]:
    area_names = area_names or {}
    bus_rows = [row for row in rows if is_bus_stop(row)]
    if not bus_rows:
        raise ValueError("No bus stop records were available to transform")

    by_area: dict[str, list[dict]] = defaultdict(list)
    for row in bus_rows:
        by_area[(row.get("AdministrativeAreaCode") or "unknown").strip() or "unknown"].append(row)

    area_summary = []
    for area_code, area_rows in sorted(by_area.items(), key=lambda item: (-len(item[1]), item[0])):
        total = len(area_rows)
        with_coordinates = sum(1 for row in area_rows if has_coordinates(row))
        with_naptan_code = sum(1 for row in area_rows if is_present(row.get("NaptanCode")))
        with_street = sum(1 for row in area_rows if is_present(row.get("Street")))
        with_indicator = sum(1 for row in area_rows if is_present(row.get("Indicator")))
        with_bearing = sum(1 for row in area_rows if is_present(row.get("Bearing")))
        with_locality = sum(1 for row in area_rows if is_present(row.get("LocalityName")))
        area_summary.append(
            {
                "administrative_area_code": area_code,
                "administrative_area_name": area_names.get(area_code, "Unknown" if area_code == "unknown" else ""),
                "stop_count": total,
                "with_coordinates": with_coordinates,
                "with_coordinates_percent": percent(with_coordinates, total),
                "with_naptan_code": with_naptan_code,
                "with_naptan_code_percent": percent(with_naptan_code, total),
                "with_street": with_street,
                "with_street_percent": percent(with_street, total),
                "with_indicator": with_indicator,
                "with_indicator_percent": percent(with_indicator, total),
                "with_bearing": with_bearing,
                "with_bearing_percent": percent(with_bearing, total),
                "with_locality": with_locality,
                "with_locality_percent": percent(with_locality, total),
            }
        )

    completeness = []
    for field, note in COMPLETENESS_NOTES.items():
        present = sum(1 for row in bus_rows if is_present(row.get(field)))
        completeness.append(
            {
                "field": field,
                "records_present": present,
                "records_missing": len(bus_rows) - present,
                "percent_present": percent(present, len(bus_rows)),
                "why_it_matters": note,
            }
        )

    duplicate_atco_codes = len(bus_rows) - len({(row.get("ATCOCode") or "").strip() for row in bus_rows if is_present(row.get("ATCOCode"))})
    named_area_count = sum(1 for row in area_summary if is_present(row["administrative_area_name"]) and row["administrative_area_code"] != "unknown")
    unnamed_area_count = sum(1 for row in area_summary if not is_present(row["administrative_area_name"]) and row["administrative_area_code"] != "unknown")
    metadata_counts = {
        "source_rows": len(rows),
        "bus_stop_rows": len(bus_rows),
        "administrative_areas": len(area_summary),
        "administrative_area_names_available": named_area_count,
        "administrative_area_names_missing": unnamed_area_count,
        "administrative_area_name_match_percent": percent(named_area_count, named_area_count + unnamed_area_count),
        "duplicate_atco_codes": duplicate_atco_codes,
        "stop_type_counts": dict(Counter((row.get("StopType") or "blank").strip() or "blank" for row in bus_rows)),
        "bus_stop_type_counts": dict(Counter((row.get("BusStopType") or "blank").strip() or "blank" for row in bus_rows)),
    }
    return area_summary, completeness, [dict(row) for row in STANDARD_READINESS], metadata_counts


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def transform() -> None:
    config = load_config()
    raw_path = Path(config["paths"]["raw_data"])
    raw_nptg_path = Path(config["paths"]["raw_nptg"])
    with raw_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    area_names = parse_area_names(raw_nptg_path)

    area_summary, completeness, readiness, counts = build_outputs(rows, area_names)

    write_csv(Path(config["paths"]["area_summary"]), area_summary, AREA_FIELDS)
    write_csv(Path(config["paths"]["completeness_summary"]), completeness, COMPLETENESS_FIELDS)
    write_csv(Path(config["paths"]["standard_readiness"]), readiness, READINESS_FIELDS)

    Path(config["paths"]["run_metadata"]).write_text(
        json.dumps(
            {
                "project_name": config["project_name"],
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_urls": [config["source"]["url"], config["source"]["nptg_url"]],
                "source_publisher": config["source"]["publisher"],
                "source_coverage": config["source"]["coverage"],
                "source_exclusions": "Northern Ireland",
                "input_row_counts": {"source_rows": counts["source_rows"], "nptg_administrative_areas": len(area_names)},
                "output_row_counts": {
                    "area_summary": len(area_summary),
                    "completeness_summary": len(completeness),
                    "standard_readiness": len(readiness),
                    "bus_stop_rows": counts["bus_stop_rows"],
                },
                "quality_counts": counts,
                "outputs": {
                    "area_summary": config["paths"]["area_summary"],
                    "completeness_summary": config["paths"]["completeness_summary"],
                    "standard_readiness": config["paths"]["standard_readiness"],
                    "report": config["paths"]["report"],
                },
                "validation_status": "not_run",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    transform()
