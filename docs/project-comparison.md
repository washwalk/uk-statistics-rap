# Project Comparison

This repository contains six compact RAP examples. They are deliberately different so that GSS users can compare publication styles, automation choices, and statistical risks.

| Project | Best used for learning | Strengths | Useful next improvements |
| --- | --- | --- | --- |
| `uk-labour-market-resilience-monitor/` | Building a lightweight indicator dashboard from time series | Simple Python-only workflow, validation script, static dashboard, clear source caveats, standard Make targets, run metadata | Add unit tests, revisions tracking, uncertainty notes, and regional breakdowns |
| `ons-retail-sales-rap/` | Producing a recurring statistical summary report | Quarto report, Makefile, tests for core calculations, raw/processed/output separation, run metadata, offline output validation | Add accessibility checks and fuller source revision reporting |
| `uk-housing-affordability-monitor/` | Combining official sources into a derived local-area indicator | Transparent indicator definition, documented filters, Quarto website, clear limitations, output validation command, run metadata | Add fuller tests, geography-change handling, and UK-wide source extensions |
| `uk-inflation-monitor/` | Building a compact time-series monitor for a high-profile indicator | Single-series API fetch, tested previous-period change, static report, run metadata, offline validation | Add basket/component breakdowns and fuller revisions notes |
| `uk-gdp-release-summary/` | Creating a recurring release-summary workflow | Tested previous-period growth calculation, release caveat, static summary, standard command contract | Add chained-volume measure variants and release-calendar checks |
| `uk-population-change-explorer/` | Validating area-period demographic outputs | Area code/name fields, positive count checks, tested derived population change, geography-style validation | Add local-authority breakdowns and geography-change handling |

## Which Example To Start From

- Use the [`template/`](../template/) starter if you want a neutral structure for a new statistic rather than copying one of the worked examples.
- Use the labour market example if you need a small HTML dashboard with simple cards and time-series indicators.
- Use the retail sales example if you need a repeatable bulletin-style report with charts, tables, and tests.
- Use the housing example if you need a public methodology page and a multi-source derived indicator.
- Use the inflation example if you need a small latest-period monitor for a single time series.
- Use the GDP example if you need previous-period growth calculations and release-summary caveats.
- Use the population example if you need area-period checks and positive-count validation.

## Common RAP Features Across The Examples

- Public official-statistics source data.
- Repeatable code-based processing.
- Clear separation between source data and analytical outputs.
- Methodology or README documentation.
- GitHub Pages publication.
- Scope and limitations stated for users.

## Current Gaps Across The Repo

- Project structure is not fully standardised even though common Make targets and metadata fields now exist.
- The compact examples now test their core calculations, but fuller publication-level regression tests are still limited.
- Accessibility checks are documented as a need but not automated.
- Revisions tracking is not yet implemented.

These gaps are useful next steps because they reflect common issues teams face when moving a prototype RAP toward a production statistical workflow.
