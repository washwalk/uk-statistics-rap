import unittest

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transform import build_outputs, is_bus_stop  # noqa: E402


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

        area, completeness, readiness, counts = build_outputs(rows)

        self.assertEqual(counts["source_rows"], 3)
        self.assertEqual(counts["bus_stop_rows"], 2)
        self.assertEqual(area[0]["administrative_area_code"], "001")
        self.assertEqual(area[0]["stop_count"], 2)
        self.assertEqual(area[0]["with_coordinates"], 1)
        self.assertEqual(area[0]["with_coordinates_percent"], "50.0")
        naptan = next(row for row in completeness if row["field"] == "NaptanCode")
        self.assertEqual(naptan["records_present"], 1)
        self.assertEqual(naptan["records_missing"], 1)
        self.assertTrue(any(row["standard_feature"] == "Covered shelter with seating" for row in readiness))
        self.assertTrue(any(row["standard_feature"] == "Lighting at bus stop" and row["national_data_status"] == "not_available" for row in readiness))
        self.assertTrue(any(row["national_data_status"] == "not_available" for row in readiness))

    def test_counts_duplicate_atco_codes(self):
        rows = [
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "001"},
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": "001"},
        ]

        _, _, _, counts = build_outputs(rows)

        self.assertEqual(counts["duplicate_atco_codes"], 1)

    def test_blank_area_code_falls_back_to_unknown(self):
        rows = [
            {"ATCOCode": "10001", "StopType": "BCT", "BusStopType": "MKD", "AdministrativeAreaCode": ""},
            {"ATCOCode": "10002", "StopType": "BCT", "BusStopType": "MKD"},
        ]

        area, _, _, _ = build_outputs(rows)

        self.assertEqual(area[0]["administrative_area_code"], "unknown")
        self.assertEqual(area[0]["stop_count"], 2)

    def test_empty_bus_records_fail(self):
        with self.assertRaises(ValueError):
            build_outputs([{"StopType": "RLY", "BusStopType": "", "AdministrativeAreaCode": "001"}])


if __name__ == "__main__":
    unittest.main()
