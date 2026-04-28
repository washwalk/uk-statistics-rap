from __future__ import annotations

import unittest

from src.transform import build_rows


class TransformTests(unittest.TestCase):
    def test_build_rows_calculates_previous_period_change(self) -> None:
        config = {"source": {"measure": "CPIH annual inflation rate", "series_id": "L55O"}}
        payload = {
            "months": [
                {"date": "2023 JAN", "value": "8.8"},
                {"date": "2023 FEB", "value": "9.2"},
                {"date": "2023 MAR", "value": "8.9"},
            ]
        }

        rows = build_rows(config, payload)

        self.assertEqual(rows[0]["change_from_previous"], "")
        self.assertEqual(rows[1]["change_from_previous"], 0.4)
        self.assertEqual(rows[2]["change_from_previous"], -0.3)
        self.assertEqual(rows[0]["source_series"], "L55O")

    def test_build_rows_rejects_payload_without_values(self) -> None:
        config = {"source": {"measure": "CPIH annual inflation rate", "series_id": "L55O"}}
        payload = {"months": [{"date": "2023 JAN", "value": ""}]}

        with self.assertRaises(ValueError):
            build_rows(config, payload)


if __name__ == "__main__":
    unittest.main()
