import unittest
from tempfile import TemporaryDirectory

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transform import build_outputs, is_bus_stop, modification_date_summary, parse_area_names  # noqa: E402


class TransformTests(unittest.TestCase):
    def test_filters_bus_records(self):
        self.assertTrue(is_bus_stop({"StopType": "BCT", "BusStopType": "MKD"}))
        self.assertTrue(is_bus_stop({"StopType": "", "BusStopType": "CUS"}))
        self.assertFalse(is_bus_stop({"StopType": "RLY", "BusStopType": ""}))

    def test_builds_area_and_completeness_outputs(self):
        rows = [
            {
                "ATCOCode": "10001",
                "NaptanCode": "abc123",
                "CommonName": "High Street",
                "Street": "High Street",
                "Indicator": "opp",
                "Bearing": "N",
                "LocalityName": "Exampleton",
                "Longitude": "-1.1",
                "Latitude": "52.1",
                "Easting": "450000",
                "Northing": "250000",
                "StopType": "BCT",
                "BusStopType": "MKD",
                "TimingStatus": "OTH",
                "AdministrativeAreaCode": "001",
            },
            {
                "ATCOCode": "10002",
                "NaptanCode": "",
                "CommonName": "Market Place",
                "Street": "",
                "Indicator": "",
                "Bearing": "S",
                "LocalityName": "Exampleton",
                "Longitude": "",
                "Latitude": "",
                "Easting": "450100",
                "Northing": "250100",
                "StopType": "BCT",
                "BusStopType": "CUS",
                "TimingStatus": "",
                "AdministrativeAreaCode": "001",
            },
            {
                "ATCOCode": "9100RAIL",
                "NaptanCode": "",
                "CommonName": "Rail Station",
                "Street": "Station Road",
                "Indicator": "",
                "Bearing": "",
                "LocalityName": "Exampleton",
                "Longitude": "-1.2",
                "Latitude": "52.2",
                "StopType": "RLY",
                "BusStopType": "",
                "TimingStatus": "",
                "AdministrativeAreaCode": "001",
            },
        ]

        area, completeness, data_dictionary, readiness, audit_requirements, example_stop_audit, counts = build_outputs(rows, {"001": "Example Area"})

        self.assertEqual(counts["source_rows"], 3)
        self.assertEqual(counts["bus_stop_rows"], 2)
        self.assertEqual(area[0]["administrative_area_code"], "001")
        self.assertEqual(area[0]["administrative_area_name"], "Example Area")
        self.assertEqual(area[0]["stop_count"], 2)
        self.assertEqual(area[0]["with_coordinates"], 1)
        self.assertEqual(area[0]["with_coordinates_percent"], "50.0")
        self.assertEqual(area[0]["with_grid_reference"], 2)
        self.assertEqual(area[0]["with_grid_reference_percent"], "100.0")
        self.assertEqual(area[0]["with_any_location_reference"], 2)
        self.assertEqual(area[0]["with_any_location_reference_percent"], "100.0")
        naptan = next(row for row in completeness if row["field"] == "NaptanCode")
        self.assertEqual(naptan["records_present"], 1)
        self.assertEqual(naptan["records_missing"], 1)
        street_definition = next(row for row in data_dictionary if row["field"] == "Street")
        self.assertIn("route coverage", street_definition["does_not_prove"])
        self.assertTrue(any(row["standard_feature"] == "Covered shelter with seating" for row in readiness))
        self.assertTrue(any(row["standard_feature"] == "Lighting at bus stop" and row["national_data_status"] == "not_available" for row in readiness))
        self.assertTrue(any(row["national_data_status"] == "not_available" for row in readiness))
        self.assertEqual({row["standard_feature"] for row in readiness}, {row["standard_feature"] for row in audit_requirements})
        lighting = next(row for row in audit_requirements if row["standard_feature"] == "Lighting at bus stop")
        self.assertIn("has_lighting", lighting["audit_field"])
        self.assertEqual(example_stop_audit[0]["atco_code"], "2400A12345")
        self.assertIn("has_shelter", example_stop_audit[0])

    def test_counts_duplicate_atco_codes(self):
        rows = [
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "001"},
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "001"},
        ]

        _, _, _, _, _, _, counts = build_outputs(rows, {"001": "Example Area"})

        self.assertEqual(counts["duplicate_atco_codes"], 1)

    def test_counts_status_and_modification_metadata(self):
        rows = [
            {
                "ATCOCode": "10001",
                "StopType": "BCT",
                "BusStopType": "MKD",
                "AdministrativeAreaCode": "001",
                "Status": "active",
                "Modification": "revise",
                "ModificationDateTime": "2026-01-02T10:00:00",
            },
            {
                "ATCOCode": "10002",
                "StopType": "BCT",
                "BusStopType": "MKD",
                "AdministrativeAreaCode": "001",
                "Status": "inactive",
                "Modification": "delete",
                "ModificationDateTime": "2025-12-31T09:00:00",
            },
            {
                "ATCOCode": "10003",
                "StopType": "BCT",
                "BusStopType": "MKD",
                "AdministrativeAreaCode": "001",
                "Status": "pending",
                "Modification": "new",
                "ModificationDateTime": "",
            },
        ]

        _, _, _, _, _, _, counts = build_outputs(rows, {"001": "Example Area"})

        self.assertEqual(counts["status_counts"], {"active": 1, "inactive": 1, "pending": 1})
        self.assertEqual(counts["modification_counts"], {"revise": 1, "delete": 1, "new": 1})
        self.assertEqual(counts["modification_datetime_summary"]["records_with_modification_datetime"], 2)
        self.assertEqual(counts["modification_datetime_summary"]["records_missing_modification_datetime"], 1)
        self.assertEqual(counts["modification_datetime_summary"]["earliest_modification_datetime"], "2025-12-31T09:00:00")
        self.assertEqual(counts["modification_datetime_summary"]["latest_modification_datetime"], "2026-01-02T10:00:00")

    def test_modification_date_summary_counts_invalid_dates_as_missing(self):
        summary = modification_date_summary(
            [
                {"ModificationDateTime": "2026-01-02T10:00:00"},
                {"ModificationDateTime": "not-a-date"},
                {"ModificationDateTime": ""},
            ]
        )

        self.assertEqual(summary["records_with_modification_datetime"], 1)
        self.assertEqual(summary["records_missing_modification_datetime"], 2)

    def test_blank_area_code_falls_back_to_unknown(self):
        rows = [
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": ""},
            {"ATCOCode": "10002", "StopType": "BCT", "BusStopType": "MKD"},
        ]

        area, _, _, _, _, _, counts = build_outputs(rows)

        self.assertEqual(area[0]["administrative_area_code"], "unknown")
        self.assertEqual(area[0]["administrative_area_name"], "Unknown")
        self.assertEqual(area[0]["stop_count"], 2)
        self.assertEqual(counts["administrative_area_names_missing"], 0)

    def test_counts_missing_area_names(self):
        rows = [
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "001"},
            {"ATCOCode": "10002", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "002"},
        ]

        area, _, _, _, _, _, counts = build_outputs(rows, {"001": "Example Area"})

        self.assertEqual(next(row for row in area if row["administrative_area_code"] == "001")["administrative_area_name"], "Example Area")
        self.assertEqual(next(row for row in area if row["administrative_area_code"] == "002")["administrative_area_name"], "")
        self.assertEqual(counts["administrative_area_names_available"], 1)
        self.assertEqual(counts["administrative_area_names_missing"], 1)
        self.assertEqual(counts["administrative_area_name_match_percent"], "50.0")

    def test_adds_quality_flags_for_review_prompts(self):
        rows = [
            {
                "ATCOCode": "10001",
                "NaptanCode": "",
                "Street": "High Street",
                "Longitude": "",
                "Latitude": "",
                "StopType": "BCT",
                "BusStopType": "MKD",
                "AdministrativeAreaCode": "001",
            }
        ]

        _, _, _, _, _, _, counts = build_outputs(rows, {"001": "Example Area"})

        flags = {row["flag"] for row in counts["quality_flags"]}
        self.assertIn("no_wgs84_coordinates", flags)
        self.assertIn("all_records_have_street", flags)
        self.assertIn("low_public_stop_code_completeness", flags)

    def test_parses_nptg_administrative_area_names(self):
        with TemporaryDirectory() as directory:
            fixture = Path(directory) / "nptg_fixture.xml"
            fixture.write_text(
                """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<NptgLocalities xmlns=\"http://www.naptan.org.uk/\">
  <AdministrativeAreas>
    <AdministrativeArea><AdministrativeAreaCode>001</AdministrativeAreaCode><Name>Example Area</Name></AdministrativeArea>
    <AdministrativeArea><AdministrativeAreaCode>002</AdministrativeAreaCode><Name>Second Area</Name></AdministrativeArea>
  </AdministrativeAreas>
</NptgLocalities>
""",
                encoding="utf-8",
            )

            self.assertEqual(parse_area_names(fixture), {"001": "Example Area", "002": "Second Area"})

    def test_empty_bus_records_fail(self):
        with self.assertRaises(ValueError):
            build_outputs([{"StopType": "RLY", "BusStopType": "", "AdministrativeAreaCode": "001"}])


if __name__ == "__main__":
    unittest.main()
