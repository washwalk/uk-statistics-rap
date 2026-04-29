# UK Bus Stop Standard Data Monitor

Compact reproducible analytical pipeline using DfT NaPTAN open data to show what can currently be monitored nationally for a proposed bus stop standard, and where the facility-data gaps are.

Published report: `https://washwalk.github.io/uk-statistics-rap/uk-bus-stop-standard-data-monitor/`

## Purpose

Campaign for Better Transport's December 2024 report, *Better Bus Stops: Creating a national bus stop standard*, makes the policy case for a national standard covering safety, legibility, accessibility and comfort.

This project does not reproduce that report. It provides a data implementation companion: a reproducible prototype showing what the current national stop register can measure and what extra local authority audit fields would be needed to monitor compliance.

## What It Tracks

- Registered bus stop records in NaPTAN for England, Scotland and Wales.
- NaPTAN register status and record-modification metadata, so active, inactive and pending records are visible without removing registered records from the base dataset.
- Bus stop counts by administrative area, with names joined from the DfT National Public Transport Gazetteer (NPTG).
- Completeness of passenger-facing and monitoring fields, including stop names, public stop codes, WGS84 coordinates, grid references where present, street, indicator, bearing and locality.
- A data dictionary explaining what each completeness metric means and what it does not prove.
- A standard-readiness matrix mapping proposed bus stop standard features to current national open-data availability.
- An audit-requirements matrix and example stop-audit template showing what local transport authorities would need to collect to monitor compliance.

## Workflow

```text
NaPTAN CSV API + NPTG XML API -> raw cache -> area/completeness/readiness/audit CSVs -> validation -> static HTML report
```

Offline tests use small fixtures and committed processed outputs. Live-source refreshes are isolated in `make integration-test` so routine assurance does not depend on network availability.

## Source

- Sources: Department for Transport National Public Transport Access Nodes (NaPTAN) and National Public Transport Gazetteer (NPTG).
- NaPTAN endpoint: `https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv`.
- NPTG endpoint: `https://naptan.api.dft.gov.uk/v1/nptg`.
- Coverage: England, Scotland and Wales. Northern Ireland is not included.
- Licence: Open Government Licence unless otherwise stated by DfT.

## Local Development

```bash
make fetch             # fetch live NaPTAN CSV and NPTG XML into data/raw/
make transform         # build processed summaries and metadata
make validate          # validate existing generated outputs only
make test              # offline unit tests and validation only
make integration-test  # refresh live NaPTAN/NPTG data, transform, and validate
make report            # refresh live data and build the static report
make clean             # remove generated raw/processed/report outputs
```

## Outputs

- Raw source response: `data/raw/source.csv`
- Raw NPTG gazetteer response: `data/raw/nptg.xml`
- Source fetch metadata: `data/raw/source-metadata.json`
- Area summary: `data/processed/area-summary.csv`
- Completeness summary: `data/processed/completeness-summary.csv`
- Data dictionary: `data/processed/data-dictionary.csv`
- Standard-readiness matrix: `data/processed/standard-readiness.csv`
- Audit-requirements matrix: `data/processed/audit-requirements.csv`
- Example stop-audit template: `examples/example-stop-audit.csv`
- Run metadata: `data/processed/run-metadata.json`
- Static report: `docs/index.html`

## Validation

`src/validate.py` checks that processed outputs and run metadata exist, required columns are present, outputs are non-empty, area stop counts sum to the metadata total, active area codes are matched to NPTG names, completeness percentages are valid, readiness statuses use expected values, expected proposed-standard features are present, audit requirements align one-to-one with readiness features, status and modification counts sum to the filtered bus stop total, quality-review prompts are recorded, and metadata output paths and row counts match the generated files.

## Assurance Evidence

- Offline evidence: `make test` checks transformation logic and validates committed processed outputs without calling the NaPTAN or NPTG APIs.
- Live-source evidence: `make integration-test` fetches the configured NaPTAN and NPTG sources, rebuilds summaries, and validates the result.
- Audit evidence: `data/processed/run-metadata.json` records source URL, input/output row counts, quality counts, outputs, and validation status.
- Reviewer evidence: `methodology.md`, the README, and the static report explain the source, transformation, validation checks, limitations, and relationship to the campaign report.

## Interpretation

The outputs are best read as a national data-readiness monitor. They show whether the national register can support implementation monitoring, not whether individual stops comply with a future standard.

Percentages are record-level field-completeness rates. For example, `Street` means the stop record has a non-blank street label; it does not mean that share of streets has a bus route. `Longitude` and `Latitude` completeness means WGS84 coordinate fields are populated; areas with 0% WGS84 completeness may still have other location references in source systems.

The monitor keeps all registered bus stop records in scope, but reports NaPTAN `Status` counts separately so active, inactive and pending records are visible. `ModificationDateTime` describes when the NaPTAN register record was modified; it is not a physical stop inspection date and does not indicate facility condition.

## Limitations

NaPTAN is a national transport reference dataset, not an official statistics release. It identifies stops and supports data-quality checks, but it does not consistently record whether stops have shelter, seating, lighting, printed timetables, route maps, QR codes, working real-time displays, cleaning schedules or repair contracts.

## Future Audit Fields

A full National Bus Stop Standard monitor would need local authority audit fields such as proposed category, shelter, seating, printed timetable, route map, RTI display, QR/weblink, lighting, accessible boarding area, cleaning programme, repair contract, condition rating, audit date and evidence URL.

This prototype publishes `data/processed/audit-requirements.csv` and `examples/example-stop-audit.csv` to make that stop-level evidence model explicit. The join key is `ATCOCode`, represented as `atco_code` in the example audit template.
