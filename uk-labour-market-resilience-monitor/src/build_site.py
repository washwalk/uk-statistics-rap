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
            <article class=\"metric\">
              <div class=\"label\">{html.escape(row['series_id'])}</div>
              <h3>{html.escape(row['indicator'])}</h3>
              <p class=\"value\">{html.escape(_format_value(row))}</p>
              <p class=\"change {class_name}\">{label}: {html.escape(_format_change(row))}</p>
              <p class=\"small\">{html.escape(row['period'])}. {html.escape(row['summary'])}</p>
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
  <header class=\"site-header\">
    <a class=\"brand\" href=\"../\">UK Statistics RAP</a>
    <nav aria-label=\"Primary navigation\">
      <a href=\"../uk-labour-market-resilience-monitor/\">Labour market</a>
      <a href=\"../ons-retail-sales-rap/\">Retail sales</a>
      <a href=\"../uk-housing-affordability-monitor/\">Housing</a>
      <a href=\"https://github.com/washwalk/uk-statistics-rap\">GitHub</a>
    </nav>
  </header>

  <main>
    <section class=\"intro\">
    <p class=\"eyebrow\">ONS labour market monitor</p>
    <h1>UK Labour Market Resilience Monitor</h1>
    <p class=\"lede\">Headline labour market signals from official ONS time series.</p>
    <p class=\"small\">Last updated: {html.escape(snapshot['generated_at'])}</p>
    </section>

    <section>
      <h2>Latest values</h2>
      <div class=\"metrics\">
        {''.join(cards)}
      </div>
    </section>

    <section class=\"panel\">
      <h2>Trend</h2>
      <p class=\"small\">Select a series to inspect the recent published trend.</p>
      <label for=\"indicatorSelect\">Indicator</label>
      <select id=\"indicatorSelect\"></select>
      <canvas id=\"trendChart\" height=\"120\"></canvas>
    </section>

    <section class=\"note\">
      <h2>Source and method</h2>
      <p>Data are rebuilt from ONS public time series. Direction labels compare the latest observation with the previous observation and should be read as monitoring signals, not forecasts.</p>
      <p><a href=\"data/indicators.json\">Download dashboard data JSON</a></p>
    </section>
  </main>
  <script src=\"assets/site.js\"></script>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html_doc, encoding="utf-8")
    print(f"Built {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    build_site()
