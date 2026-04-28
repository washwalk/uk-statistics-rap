from __future__ import annotations

import unittest

from src.transform import build_rows, source_points


class TransformTests(unittest.TestCase):
    def test_build_rows_calculates_population_changes(self) -> None:
        config = {"source": {"measure": "UK population estimate", "series_id": "UKPOP"}}
        payload = {
            "years": [
                {"date": "2021", "value": "67,000,000"},
                {"date": "2022", "value": "67,500,000"},
            ]
        }

        rows = build_rows(config, payload)

        self.assertEqual(rows[0]["population"], 67000000)
        self.assertEqual(rows[0]["change_from_previous"], "")
        self.assertEqual(rows[1]["change_from_previous"], 500000)
        self.assertEqual(rows[1]["percent_change_from_previous"], 0.746)
        self.assertEqual(rows[0]["area_code"], "K02000001")
        self.assertEqual(rows[0]["source_series"], "UKPOP")

    def test_build_rows_rejects_payload_without_values(self) -> None:
        config = {"source": {"measure": "UK population estimate", "series_id": "UKPOP"}}
        payload = {"years": [{"date": "2021", "value": ""}]}

        with self.assertRaises(ValueError):
            build_rows(config, payload)

    def test_source_points_prefers_annual_observations(self) -> None:
        period_type, points = source_points({"months": [{"date": "2021 JAN", "value": "1"}], "years": [{"date": "2021", "value": "67000000"}]})

        self.assertEqual(period_type, "years")
        self.assertEqual(points[0]["date"], "2021")

    def test_build_rows_rejects_non_numeric_values(self) -> None:
        config = {"source": {"measure": "UK population estimate", "series_id": "UKPOP"}}
        payload = {"years": [{"date": "2021", "value": "not numeric"}]}

        with self.assertRaises(ValueError):
            build_rows(config, payload)


if __name__ == "__main__":
    unittest.main()
