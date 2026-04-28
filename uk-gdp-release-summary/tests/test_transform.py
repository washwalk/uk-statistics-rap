from __future__ import annotations

import unittest

from src.transform import build_rows


class TransformTests(unittest.TestCase):
    def test_build_rows_calculates_previous_period_growth(self) -> None:
        config = {"source": {"measure": "GDP chained volume measure index", "series_id": "ABMI"}}
        payload = {
            "quarters": [
                {"date": "2022 Q1", "value": "100.0"},
                {"date": "2022 Q2", "value": "101.0"},
                {"date": "2022 Q3", "value": "100.5"},
            ]
        }

        rows = build_rows(config, payload)

        self.assertEqual(rows[0]["growth_from_previous_percent"], "")
        self.assertEqual(rows[1]["growth_from_previous_percent"], 1.0)
        self.assertEqual(rows[2]["growth_from_previous_percent"], -0.495)
        self.assertEqual(rows[0]["source_series"], "ABMI")

    def test_build_rows_skips_growth_when_previous_value_is_zero(self) -> None:
        config = {"source": {"measure": "GDP chained volume measure index", "series_id": "ABMI"}}
        payload = {"quarters": [{"date": "2022 Q1", "value": "0"}, {"date": "2022 Q2", "value": "1"}]}

        rows = build_rows(config, payload)

        self.assertEqual(rows[1]["growth_from_previous_percent"], "")


if __name__ == "__main__":
    unittest.main()
