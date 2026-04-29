from __future__ import annotations

import csv
import json
from pathlib import Path


AREA_COLUMNS = {
    "administrative_area_code",
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
}
COMPLETENESS_COLUMNS = {"field", "records_present", "records_missing", "percent_present", "why_it_matters"}
READINESS_COLUMNS = {"standard_feature", "cbt_category_requirement", "national_data_status", "available_fields", "monitoring_note"}
REQUIRED_METADATA = {"project_name", "run_timestamp", "source_urls", "input_row_counts", "output_row_counts", "quality_counts", "outputs", "validation_status"}
EXPECTED_READINESS_FEATURES = {
    "Bus stop identity and location",
    "Bus stop flag with stop name, route numbers, destination and branding",
    "Printed timetable of arrival times",
    "Covered shelter with seating",
    "Map of local bus stops and route network",
    "Real-time next bus information display",
    "QR code or weblink to online real-time passenger information",
    "Lighting at bus stop",
    "Cleaning, inspection, repair and maintenance arrangements",
}
READINESS_STATUSES = {"available", "partial", "not_available"}
AREA_COUNT_PERCENT_PAIRS = (
    ("with_coordinates", "with_coordinates_percent"),
    ("with_naptan_code", "with_naptan_code_percent"),
    ("with_street", "with_street_percent"),
    ("with_indicator", "with_indicator_percent"),
    ("with_bearing", "with_bearing_percent"),
    ("with_locality", "with_locality_percent"),
)


def load_config() -> dict:
    return json.loads(Path("config.json").read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def require_numeric_percent(value: str, label: str, errors: list[str]) -> None:
    try:
        number = float(value)
    except ValueError:
        errors.append(f"{label} is not numeric")
        return
    if number < 0 or number > 100:
        errors.append(f"{label} is outside 0 to 100")


def expected_percent(part: int, total: int) -> str:
    if total == 0:
        return "0.0"
    return f"{(part / total) * 100:.1f}"


def validate() -> None:
    config = load_config()
    errors: list[str] = []
    area_rows: list[dict] = []
    completeness_rows: list[dict] = []
    readiness_rows: list[dict] = []
    metadata: dict = {}

    area_path = Path(config["paths"]["area_summary"])
    completeness_path = Path(config["paths"]["completeness_summary"])
    readiness_path = Path(config["paths"]["standard_readiness"])
    metadata_path = Path(config["paths"]["run_metadata"])

    for path, columns, label in (
        (area_path, AREA_COLUMNS, "Area summary"),
        (completeness_path, COMPLETENESS_COLUMNS, "Completeness summary"),
        (readiness_path, READINESS_COLUMNS, "Standard readiness"),
    ):
        if not path.exists():
            errors.append(f"Missing {label.lower()}: {path}")
            continue
        rows, fieldnames = read_csv(path)
        missing = columns.difference(fieldnames)
        if missing:
            errors.append(f"{label} missing columns: {sorted(missing)}")
        if not rows:
            errors.append(f"{label} is empty")
        if label == "Area summary":
            area_rows = rows
        elif label == "Completeness summary":
            completeness_rows = rows
        else:
            readiness_rows = rows

    total_area_stops = 0
    seen_areas: set[str] = set()
    for row in area_rows:
        area_code = row.get("administrative_area_code", "")
        if not area_code:
            errors.append("Area summary contains blank administrative area code")
        if area_code in seen_areas:
            errors.append(f"Area summary contains duplicate area code {area_code}")
        seen_areas.add(area_code)
        try:
            stop_count = int(row["stop_count"])
        except ValueError:
            errors.append(f"Stop count is not an integer for area {area_code}")
            continue
        if stop_count <= 0:
            errors.append(f"Stop count is not positive for area {area_code}")
        total_area_stops += stop_count
        for count_field, percent_field in AREA_COUNT_PERCENT_PAIRS:
            try:
                count = int(row[count_field])
            except ValueError:
                errors.append(f"{count_field} is not an integer for area {area_code}")
                continue
            if count < 0 or count > stop_count:
                errors.append(f"{count_field} is outside 0 to stop_count for area {area_code}")
            require_numeric_percent(row.get(percent_field, ""), f"{percent_field} for area {area_code}", errors)
            if row.get(percent_field) != expected_percent(count, stop_count):
                errors.append(f"{percent_field} does not match {count_field} for area {area_code}")

    completeness_fields = {row.get("field", "") for row in completeness_rows}
    for expected in ("ATCOCode", "NaptanCode", "CommonName", "Longitude", "Latitude", "BusStopType"):
        if expected not in completeness_fields:
            errors.append(f"Completeness summary missing expected field {expected}")
    metadata_bus_stop_rows = None
    if metadata_path.exists():
        try:
            metadata_preview = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata_bus_stop_rows = metadata_preview.get("output_row_counts", {}).get("bus_stop_rows")
        except json.JSONDecodeError:
            metadata_bus_stop_rows = None

    for row in completeness_rows:
        require_numeric_percent(row.get("percent_present", ""), f"percent_present for field {row.get('field')}", errors)
        try:
            present = int(row["records_present"])
            missing = int(row["records_missing"])
        except ValueError:
            errors.append(f"Completeness counts are not integers for field {row.get('field')}")
            continue
        if present < 0 or missing < 0:
            errors.append(f"Completeness counts are negative for field {row.get('field')}")
        if metadata_bus_stop_rows is not None and present + missing != metadata_bus_stop_rows:
            errors.append(f"Completeness counts do not sum to bus stop rows for field {row.get('field')}")

    readiness_feature_list = [row.get("standard_feature", "") for row in readiness_rows]
    readiness_features = set(readiness_feature_list)
    duplicate_features = sorted(feature for feature in readiness_features if readiness_feature_list.count(feature) > 1)
    if duplicate_features:
        errors.append(f"Standard readiness contains duplicate features: {duplicate_features}")
    missing_features = EXPECTED_READINESS_FEATURES.difference(readiness_features)
    if missing_features:
        errors.append(f"Standard readiness missing expected features: {sorted(missing_features)}")
    statuses = {row.get("national_data_status", "") for row in readiness_rows}
    unexpected_statuses = statuses.difference(READINESS_STATUSES)
    if unexpected_statuses:
        errors.append(f"Standard readiness has unexpected statuses: {sorted(unexpected_statuses)}")
    if not any(row.get("national_data_status") == "not_available" for row in readiness_rows):
        errors.append("Standard readiness does not identify any national data gaps")

    if not metadata_path.exists():
        errors.append(f"Missing run metadata: {metadata_path}")
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        missing = REQUIRED_METADATA.difference(metadata)
        if missing:
            errors.append(f"Run metadata missing keys: {sorted(missing)}")
        if metadata.get("project_name") != config["project_name"]:
            errors.append("Run metadata project name does not match config")
        if config["source"]["url"] not in metadata.get("source_urls", []):
            errors.append("Run metadata does not include configured source URL")
        outputs = metadata.get("outputs", {})
        if outputs.get("area_summary") != config["paths"]["area_summary"]:
            errors.append("Run metadata area summary output path does not match config")
        if outputs.get("completeness_summary") != config["paths"]["completeness_summary"]:
            errors.append("Run metadata completeness summary output path does not match config")
        if outputs.get("standard_readiness") != config["paths"]["standard_readiness"]:
            errors.append("Run metadata standard readiness output path does not match config")
        if outputs.get("report") != config["paths"]["report"]:
            errors.append("Run metadata report output path does not match config")
        output_counts = metadata.get("output_row_counts", {})
        if output_counts.get("area_summary") != len(area_rows):
            errors.append("Run metadata area summary row count does not match output")
        if output_counts.get("completeness_summary") != len(completeness_rows):
            errors.append("Run metadata completeness row count does not match output")
        if output_counts.get("standard_readiness") != len(readiness_rows):
            errors.append("Run metadata readiness row count does not match output")
        if output_counts.get("bus_stop_rows") != total_area_stops:
            errors.append("Area stop counts do not sum to metadata bus stop row count")
        quality_counts = metadata.get("quality_counts", {})
        if "duplicate_atco_codes" not in quality_counts:
            errors.append("Run metadata does not record duplicate ATCO code count")
        if metadata.get("validation_status") not in {"not_run", "passed"}:
            errors.append("Run metadata validation status must be not_run or passed")

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    if metadata_path.exists() and metadata:
        metadata["validation_status"] = "passed"
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print("Validation passed")


if __name__ == "__main__":
    validate()
