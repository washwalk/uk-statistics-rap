from __future__ import annotations

import html
import json

from config import DOCS_DIR, PROCESSED_DIR


def _format_value(row: dict) -> str:
    value = float(row["value"])
    unit = row["unit"]
    if unit == "%":
        return f"{value:.1f}%"
    if unit == "thousands":
        return f"{value:,.0f}k"
    return f"{value:,.1f} {unit}"


def _format_change(row: dict) -> str:
    change = row.get("change")
    if change is None:
        return "No previous observation available"
    unit = "percentage points" if row["unit"] == "%" else row["unit"]
    sign = "+" if float(change) > 0 else ""
    return f"{sign}{float(change):.1f} {unit} since previous observation"


def _signal(row: dict) -> tuple[str, str]:
    change = row.get("change")
    direction = row.get("direction")
    if change is None or direction == "context" or abs(float(change)) < 0.05:
        return "Neutral", "neutral"
    improved = float(change) > 0 if direction == "higher_is_better" else float(change) < 0
    return ("Improving", "good") if improved else ("Weakening", "risk")


def build_site() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads((PROCESSED_DIR / "latest_snapshot.json").read_text(encoding="utf-8"))
    cards = []

    for row in snapshot["indicators"]:
        label, class_name = _signal(row)
        cards.append(
            f"""
            <article class=\"card\">
              <div class=\"card-topline\">{html.escape(row['series_id'])}</div>
              <h3>{html.escape(row['indicator'])}</h3>
              <p class=\"value\">{html.escape(_format_value(row))}</p>
              <p>{html.escape(row['period'])}</p>
              <p>{html.escape(_format_change(row))}</p>
              <p><span class=\"pill {class_name}\">{label}</span></p>
              <p class=\"small\">{html.escape(row['summary'])}</p>
            </article>
            """
        )

    html_doc = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>UK Labour Market Resilience Monitor</title>
  <link rel=\"stylesheet\" href=\"assets/style.css\">
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
</head>
<body>
  <header class=\"hero\">
    <p class=\"eyebrow\">ONS API automated monitor</p>
    <h1>UK Labour Market Resilience Monitor</h1>
    <p class=\"lede\">A reproducible dashboard tracking headline labour market signals from official ONS time series.</p>
    <p class=\"small\">Generated: {html.escape(snapshot['generated_at'])}</p>
  </header>

  <main>
    <section>
      <h2>Latest Snapshot</h2>
      <div class=\"cards\">
        {''.join(cards)}
      </div>
    </section>

    <section class=\"panel\">
      <h2>Trend Explorer</h2>
      <p>Select an indicator to inspect the published ONS series used in the monitor.</p>
      <label for=\"indicatorSelect\">Indicator</label>
      <select id=\"indicatorSelect\"></select>
      <canvas id=\"trendChart\" height=\"120\"></canvas>
    </section>

    <section class=\"grid-two\">
      <div>
        <h2>How To Read This</h2>
        <p>The monitor uses simple direction checks between the latest and previous observations. It is designed as an accessible signal panel, not a forecast or causal model.</p>
      </div>
      <div>
        <h2>Quality Notes</h2>
        <p>Outputs are rebuilt from ONS source data, validated for expected structure and numeric values, and published as static files. Labour market statistics may be revised, so the latest run should be treated as the current reproducible view.</p>
      </div>
    </section>

    <section>
      <h2>Sources</h2>
      <p>Data are from ONS public time series. See the project README and methodology for definitions, transformations, validation rules, and limitations.</p>
      <p><a href=\"../methodology.md\">Methodology</a> | <a href=\"data/indicators.json\">Dashboard data JSON</a></p>
    </section>
  </main>

  <footer>
    <p>Built as a reproducible analytical pipeline for a GSS interview portfolio project. ONS content is available under the Open Government Licence unless otherwise stated.</p>
  </footer>
  <script src=\"assets/site.js\"></script>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html_doc, encoding="utf-8")
    print(f"Built {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    build_site()
