from __future__ import annotations

import pandas as pd


def test_value_column_can_be_numeric() -> None:
    values = pd.to_numeric(pd.Series(["1", "2.5", "3"]), errors="coerce")

    assert values.notna().all()
    assert values.tolist() == [1.0, 2.5, 3.0]
