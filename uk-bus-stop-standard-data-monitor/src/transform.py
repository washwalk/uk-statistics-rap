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
    "with_grid_reference",
    "with_grid_reference_percent",
    "with_any_location_reference",
    "with_any_location_reference_percent",
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
BODS_SUMMARY_FIELDS = ["metric", "value", "source", "note"]
BODS_AREA_FIELDS = [
    "administrative_area_code",
    "administrative_area_name",
    "bods_timetable_dataset_count",
    "evidence_level",
    "caveat",
]

COMPLETENESS_FIELDS = ["field", "records_present", "records_missing", "percent_present", "why_it_matters"]
DATA_DICTIONARY_FIELDS = ["field", "source", "monitor_interpretation", "does_not_prove"]
READINESS_FIELDS = ["standard_feature", "cbt_category_requirement", "national_data_status", "available_fields", "monitoring_note"]
AUDIT_REQUIREMENT_FIELDS = ["standard_feature", "audit_field", "field_type", "collection_level", "why_needed", "example_values"]
EXAMPLE_STOP_AUDIT_FIELDS = [
    "atco_code",
    "audit_date",
    "auditing_body",
    "proposed_standard_category",
    "has_clear_stop_flag",
    "displayed_route_numbers",
    "displayed_destinations",
    "has_shelter",
    "has_seating",
    "shelter_condition_rating",
    "has_printed_timetable",
    "timetable_last_checked_date",
    "has_route_map",
    "route_map_last_checked_date",
    "has_rti_display",
    "rti_display_working",
    "rti_last_checked_datetime",
    "has_qr_or_weblink",
    "qr_or_weblink_target",
    "qr_or_weblink_working",
    "has_lighting",
    "lighting_working",
    "lighting_ownership",
    "has_cleaning_programme",
    "has_repair_contract",
    "inspection_frequency",
    "condition_rating",
    "evidence_url",
    "notes",
]

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

DATA_DICTIONARY = [
    {
        "field": "ATCOCode",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Unique stop identifier available for linking records across systems.",
        "does_not_prove": "That the physical stop is present, accessible, maintained or compliant.",
    },
    {
        "field": "NaptanCode",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Public-facing stop code is populated on the stop record.",
        "does_not_prove": "That the code is displayed on the physical stop flag or passenger information board.",
    },
    {
        "field": "CommonName",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Passenger-facing stop name is populated.",
        "does_not_prove": "That the physical stop flag is present, correct or legible.",
    },
    {
        "field": "Street",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Street-name field is populated on the stop record.",
        "does_not_prove": "The share of streets served by buses, route coverage, or the quality of the street label.",
    },
    {
        "field": "Indicator",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Qualifier such as opposite, outside, bay or stop number is populated.",
        "does_not_prove": "That the qualifier is visible at the stop or sufficient for wayfinding.",
    },
    {
        "field": "Bearing",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Direction of travel at the stop is populated.",
        "does_not_prove": "That route destinations are displayed on the physical stop flag.",
    },
    {
        "field": "Longitude/Latitude",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "WGS84 coordinate fields are populated for mapping and spatial checks.",
        "does_not_prove": "That coordinates are spatially accurate or that other location references are absent.",
    },
    {
        "field": "Grid reference",
        "source": "NaPTAN access nodes where present",
        "monitor_interpretation": "Alternative easting/northing location fields are populated where supplied by the source schema.",
        "does_not_prove": "That WGS84 longitude/latitude fields are populated or that the location has been quality assured.",
    },
    {
        "field": "BusStopType",
        "source": "NaPTAN access nodes",
        "monitor_interpretation": "Broad physical stop type is populated.",
        "does_not_prove": "That shelter, seating, lighting or real-time displays are provided.",
    },
    {
        "field": "AdministrativeAreaCode",
        "source": "NaPTAN access nodes joined to NPTG",
        "monitor_interpretation": "Stop can be grouped to an official NPTG administrative area name.",
        "does_not_prove": "Local authority ownership, maintenance responsibility or standard compliance.",
    },
]

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

AUDIT_REQUIREMENTS = [
    {
        "standard_feature": "Bus stop identity and location",
        "audit_field": "atco_code; audit_date; auditing_body; evidence_url",
        "field_type": "identifier; date; text; url",
        "collection_level": "Stop-level audit joined to NaPTAN using ATCOCode",
        "why_needed": "Confirms the audited asset can be linked back to the national stop register and evidence trail.",
        "example_values": "2400A12345; 2026-04-29; Example Council; https://example.org/evidence/2400A12345",
    },
    {
        "standard_feature": "Bus stop flag with stop name, route numbers, destination and branding",
        "audit_field": "has_clear_stop_flag; displayed_route_numbers; displayed_destinations",
        "field_type": "boolean; text; text",
        "collection_level": "Stop-level physical audit",
        "why_needed": "NaPTAN records names and codes, but not whether the physical flag is present, legible, branded, or displaying route information.",
        "example_values": "true; 12|27|89; City centre|Hospital",
    },
    {
        "standard_feature": "Printed timetable of arrival times",
        "audit_field": "has_printed_timetable; timetable_last_checked_date",
        "field_type": "boolean; date",
        "collection_level": "Stop-level physical audit",
        "why_needed": "Confirms whether an up-to-date printed timetable is displayed at the stop.",
        "example_values": "true; 2026-04-29",
    },
    {
        "standard_feature": "Covered shelter with seating",
        "audit_field": "has_shelter; has_seating; shelter_condition_rating",
        "field_type": "boolean; boolean; category",
        "collection_level": "Stop-level physical audit",
        "why_needed": "National open data does not consistently record shelter or seating provision or condition.",
        "example_values": "true; true; good",
    },
    {
        "standard_feature": "Map of local bus stops and route network",
        "audit_field": "has_route_map; route_map_last_checked_date",
        "field_type": "boolean; date",
        "collection_level": "Stop-level physical audit",
        "why_needed": "Confirms whether route maps are displayed and recently checked.",
        "example_values": "false;",
    },
    {
        "standard_feature": "Real-time next bus information display",
        "audit_field": "has_rti_display; rti_display_working; rti_last_checked_datetime",
        "field_type": "boolean; boolean; datetime",
        "collection_level": "Stop-level physical audit or asset management system",
        "why_needed": "Confirms whether a real-time display exists and was working at audit time.",
        "example_values": "true; true; 2026-04-29T10:30:00Z",
    },
    {
        "standard_feature": "QR code or weblink to online real-time passenger information",
        "audit_field": "has_qr_or_weblink; qr_or_weblink_target; qr_or_weblink_working",
        "field_type": "boolean; url; boolean",
        "collection_level": "Stop-level physical audit",
        "why_needed": "Confirms whether physical digital-access information is provided and usable.",
        "example_values": "true; https://example.org/stop/2400A12345; true",
    },
    {
        "standard_feature": "Lighting at bus stop",
        "audit_field": "has_lighting; lighting_working; lighting_ownership",
        "field_type": "boolean; boolean; category",
        "collection_level": "Stop-level physical audit or asset management system",
        "why_needed": "NaPTAN does not record whether lighting exists, is working, or who maintains it.",
        "example_values": "true; true; highway_authority",
    },
    {
        "standard_feature": "Cleaning, inspection, repair and maintenance arrangements",
        "audit_field": "has_cleaning_programme; has_repair_contract; inspection_frequency; condition_rating",
        "field_type": "boolean; boolean; category; category",
        "collection_level": "Local authority asset management system linked to stop-level audit",
        "why_needed": "Confirms whether maintenance arrangements exist and records current asset condition.",
        "example_values": "true; true; monthly; fair",
    },
]

EXAMPLE_STOP_AUDIT = [
    {
        "atco_code": "2400A12345",
        "audit_date": "2026-04-29",
        "auditing_body": "Example Council",
        "proposed_standard_category": "Category 2",
        "has_clear_stop_flag": "true",
        "displayed_route_numbers": "12|27|89",
        "displayed_destinations": "City centre|Hospital",
        "has_shelter": "true",
        "has_seating": "true",
        "shelter_condition_rating": "good",
        "has_printed_timetable": "true",
        "timetable_last_checked_date": "2026-04-29",
        "has_route_map": "false",
        "route_map_last_checked_date": "",
        "has_rti_display": "true",
        "rti_display_working": "true",
        "rti_last_checked_datetime": "2026-04-29T10:30:00Z",
        "has_qr_or_weblink": "true",
        "qr_or_weblink_target": "https://example.org/stop/2400A12345",
        "qr_or_weblink_working": "true",
        "has_lighting": "true",
        "lighting_working": "true",
        "lighting_ownership": "highway_authority",
        "has_cleaning_programme": "true",
        "has_repair_contract": "true",
        "inspection_frequency": "monthly",
        "condition_rating": "fair",
        "evidence_url": "https://example.org/evidence/2400A12345",
        "notes": "Illustrative row only; replace with local audit evidence.",
    }
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


def has_grid_reference(row: dict) -> bool:
    pairs = (("Easting", "Northing"), ("GridEasting", "GridNorthing"), ("X", "Y"))
    return any(is_present(row.get(easting)) and is_present(row.get(northing)) for easting, northing in pairs)


def normalise_category(value: str | None) -> str:
    return (value or "blank").strip().lower() or "blank"


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


def load_json_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected {path} to contain a JSON list")
    return [row for row in payload if isinstance(row, dict)]


def value_for(row: dict, *names: str) -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def normalise_status(row: dict) -> str:
    return normalise_category(value_for(row, "status", "Status"))


def extract_admin_areas(row: dict) -> list[dict]:
    for name in ("admin_areas", "adminAreas", "adminAreasServed"):
        value = row.get(name)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def build_bods_outputs(config: dict, area_names: dict[str, str]) -> tuple[list[dict], list[dict], dict] | None:
    paths = config["paths"]
    timetables = load_json_rows(Path(paths["raw_bods_timetables"]))
    location_feeds = load_json_rows(Path(paths["raw_bods_location_feeds"]))
    fares = load_json_rows(Path(paths["raw_bods_fares"]))
    if not any((timetables, location_feeds, fares)):
        return None

    published_timetables = sum(1 for row in timetables if normalise_status(row) == "published")
    published_location_feeds = sum(1 for row in location_feeds if normalise_status(row) == "published")
    published_fares = sum(1 for row in fares if normalise_status(row) == "published")
    bods_summary = [
        {"metric": "timetable_datasets", "value": len(timetables), "source": "BODS timetables API", "note": "Dataset metadata rows fetched from BODS."},
        {"metric": "published_timetable_datasets", "value": published_timetables, "source": "BODS timetables API", "note": "Published timetable metadata does not prove printed timetable display at stops."},
        {"metric": "location_feeds", "value": len(location_feeds), "source": "BODS location feeds API", "note": "Location-feed metadata does not prove physical RTI displays exist or work."},
        {"metric": "published_location_feeds", "value": published_location_feeds, "source": "BODS location feeds API", "note": "Published AVL data is service-data evidence, not stop-facility evidence."},
        {"metric": "fare_datasets", "value": len(fares), "source": "BODS fares API", "note": "Fares metadata is contextual and not facilities evidence."},
        {"metric": "published_fare_datasets", "value": published_fares, "source": "BODS fares API", "note": "Published fares data does not evidence bus stop condition or maintenance."},
    ]

    area_counts: Counter[str] = Counter()
    for row in timetables:
        for area in extract_admin_areas(row):
            area_code = value_for(area, "atco_code", "atcoCode", "code")
            if area_code:
                area_counts[area_code] += 1

    bods_area_summary = [
        {
            "administrative_area_code": area_code,
            "administrative_area_name": area_names.get(area_code, ""),
            "bods_timetable_dataset_count": count,
            "evidence_level": "area_catalogue_metadata",
            "caveat": "BODS area metadata indicates service-data publication context; it is not stop-level facilities evidence.",
        }
        for area_code, count in sorted(area_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    metadata = {
        "bods_input_row_counts": {
            "timetables": len(timetables),
            "location_feeds": len(location_feeds),
            "fares": len(fares),
        },
        "bods_area_count": len(bods_area_summary),
        "bods_status_counts": {
            "timetables": dict(Counter(normalise_status(row) for row in timetables)),
            "location_feeds": dict(Counter(normalise_status(row) for row in location_feeds)),
            "fares": dict(Counter(normalise_status(row) for row in fares)),
        },
    }
    return bods_summary, bods_area_summary, metadata


def modification_date_summary(rows: list[dict]) -> dict:
    parsed_dates = []
    missing = 0
    for row in rows:
        value = (row.get("ModificationDateTime") or "").strip()
        if not value:
            missing += 1
            continue
        try:
            parsed_dates.append(datetime.fromisoformat(value.replace("Z", "+00:00")))
        except ValueError:
            missing += 1
    return {
        "records_with_modification_datetime": len(parsed_dates),
        "records_missing_modification_datetime": missing,
        "earliest_modification_datetime": min(parsed_dates).isoformat() if parsed_dates else "",
        "latest_modification_datetime": max(parsed_dates).isoformat() if parsed_dates else "",
    }


def build_outputs(rows: list[dict], area_names: dict[str, str] | None = None) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[dict], dict]:
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
        with_grid_reference = sum(1 for row in area_rows if has_grid_reference(row))
        with_any_location_reference = sum(1 for row in area_rows if has_coordinates(row) or has_grid_reference(row))
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
                "with_grid_reference": with_grid_reference,
                "with_grid_reference_percent": percent(with_grid_reference, total),
                "with_any_location_reference": with_any_location_reference,
                "with_any_location_reference_percent": percent(with_any_location_reference, total),
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
    quality_flags = []
    for row in area_summary:
        if row["with_coordinates_percent"] == "0.0":
            quality_flags.append({"area_code": row["administrative_area_code"], "area_name": row["administrative_area_name"], "flag": "no_wgs84_coordinates", "note": "No filtered bus stop records have both Longitude and Latitude populated."})
        if row["with_street_percent"] == "100.0":
            quality_flags.append({"area_code": row["administrative_area_code"], "area_name": row["administrative_area_name"], "flag": "all_records_have_street", "note": "Every filtered bus stop record has a non-blank Street field; this is field completeness, not street or route coverage."})
        if float(row["with_naptan_code_percent"]) < 90:
            quality_flags.append({"area_code": row["administrative_area_code"], "area_name": row["administrative_area_name"], "flag": "low_public_stop_code_completeness", "note": "Fewer than 90 percent of filtered bus stop records have a public-facing NaptanCode."})
    metadata_counts = {
        "source_rows": len(rows),
        "bus_stop_rows": len(bus_rows),
        "administrative_areas": len(area_summary),
        "administrative_area_names_available": named_area_count,
        "administrative_area_names_missing": unnamed_area_count,
        "administrative_area_name_match_percent": percent(named_area_count, named_area_count + unnamed_area_count),
        "duplicate_atco_codes": duplicate_atco_codes,
        "status_counts": dict(Counter(normalise_category(row.get("Status")) for row in bus_rows)),
        "modification_counts": dict(Counter(normalise_category(row.get("Modification")) for row in bus_rows)),
        "modification_datetime_summary": modification_date_summary(bus_rows),
        "stop_type_counts": dict(Counter((row.get("StopType") or "blank").strip() or "blank" for row in bus_rows)),
        "bus_stop_type_counts": dict(Counter((row.get("BusStopType") or "blank").strip() or "blank" for row in bus_rows)),
        "quality_flags": quality_flags,
    }
    return (
        area_summary,
        completeness,
        [dict(row) for row in DATA_DICTIONARY],
        [dict(row) for row in STANDARD_READINESS],
        [dict(row) for row in AUDIT_REQUIREMENTS],
        [dict(row) for row in EXAMPLE_STOP_AUDIT],
        metadata_counts,
    )


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
    raw_metadata_path = Path(config["paths"]["raw_metadata"])
    raw_bods_metadata_path = Path(config["paths"]["raw_bods_metadata"])
    with raw_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    area_names = parse_area_names(raw_nptg_path)
    source_fetch_metadata = {}
    if raw_metadata_path.exists():
        source_fetch_metadata = json.loads(raw_metadata_path.read_text(encoding="utf-8"))
    bods_fetch_metadata = {}
    if raw_bods_metadata_path.exists():
        bods_fetch_metadata = json.loads(raw_bods_metadata_path.read_text(encoding="utf-8"))

    area_summary, completeness, data_dictionary, readiness, audit_requirements, example_stop_audit, counts = build_outputs(rows, area_names)
    bods_outputs = build_bods_outputs(config, area_names)
    bods_metadata = {}
    if bods_outputs:
        bods_summary, bods_area_summary, bods_metadata = bods_outputs
        write_csv(Path(config["paths"]["bods_summary"]), bods_summary, BODS_SUMMARY_FIELDS)
        write_csv(Path(config["paths"]["bods_area_summary"]), bods_area_summary, BODS_AREA_FIELDS)

    write_csv(Path(config["paths"]["area_summary"]), area_summary, AREA_FIELDS)
    write_csv(Path(config["paths"]["completeness_summary"]), completeness, COMPLETENESS_FIELDS)
    write_csv(Path(config["paths"]["data_dictionary"]), data_dictionary, DATA_DICTIONARY_FIELDS)
    write_csv(Path(config["paths"]["standard_readiness"]), readiness, READINESS_FIELDS)
    write_csv(Path(config["paths"]["audit_requirements"]), audit_requirements, AUDIT_REQUIREMENT_FIELDS)
    write_csv(Path(config["paths"]["example_stop_audit"]), example_stop_audit, EXAMPLE_STOP_AUDIT_FIELDS)

    Path(config["paths"]["run_metadata"]).write_text(
        json.dumps(
            {
                "project_name": config["project_name"],
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_urls": [config["source"]["url"], config["source"]["nptg_url"]],
                "source_publisher": config["source"]["publisher"],
                "source_coverage": config["source"]["coverage"],
                "source_exclusions": "Northern Ireland",
                "source_fetch_metadata": source_fetch_metadata,
                "bods_fetch_metadata": bods_fetch_metadata,
                "input_row_counts": {"source_rows": counts["source_rows"], "nptg_administrative_areas": len(area_names)},
                "output_row_counts": {
                    "area_summary": len(area_summary),
                    "completeness_summary": len(completeness),
                    "data_dictionary": len(data_dictionary),
                    "standard_readiness": len(readiness),
                    "audit_requirements": len(audit_requirements),
                    "example_stop_audit": len(example_stop_audit),
                    "bus_stop_rows": counts["bus_stop_rows"],
                    "bods_summary": len(bods_summary) if bods_outputs else 0,
                    "bods_area_summary": len(bods_area_summary) if bods_outputs else 0,
                },
                "quality_counts": counts,
                "bods_quality_counts": bods_metadata,
                "outputs": {
                    "area_summary": config["paths"]["area_summary"],
                    "completeness_summary": config["paths"]["completeness_summary"],
                    "data_dictionary": config["paths"]["data_dictionary"],
                    "standard_readiness": config["paths"]["standard_readiness"],
                    "audit_requirements": config["paths"]["audit_requirements"],
                    "example_stop_audit": config["paths"]["example_stop_audit"],
                    "bods_summary": config["paths"]["bods_summary"],
                    "bods_area_summary": config["paths"]["bods_area_summary"],
                    "validation_results": config["paths"]["validation_results"],
                    "report": config["paths"]["report"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    transform()
