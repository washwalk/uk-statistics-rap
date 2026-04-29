# Methodology

## Source

The pipeline uses the Department for Transport National Public Transport Access Nodes (NaPTAN) API and National Public Transport Gazetteer (NPTG) API. NaPTAN is the national register of public transport access points in England, Scotland and Wales. NPTG supplies the official administrative area names used to make area-code outputs readable.

The configured sources are `https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv` and `https://naptan.api.dft.gov.uk/v1/nptg`.

## Processing

The live NaPTAN CSV is stored unchanged in `data/raw/source.csv`. The live NPTG XML is stored unchanged in `data/raw/nptg.xml`. The transform step reads the NaPTAN CSV and filters to bus-related records where `StopType` begins with `BC` or `BusStopType` is populated.

Administrative area names are parsed from NPTG `AdministrativeArea` records and joined to stop summaries using `AdministrativeAreaCode`. Names are used for interpretation only; stop counts and completeness measures are calculated from filtered NaPTAN bus stop records.

The pipeline then produces three processed outputs:

- `area-summary.csv`: stop counts and selected completeness rates by administrative area code and NPTG area name.
- `completeness-summary.csv`: national completeness rates for fields that support passenger information and monitoring.
- `data-dictionary.csv`: definitions of key fields, their monitor interpretation and what they do not prove.
- `standard-readiness.csv`: a matrix mapping proposed National Bus Stop Standard features to current national open-data availability.

## Completeness Measures

Completeness is calculated as the share of filtered bus stop records where a field is non-blank. The monitor focuses on fields relevant to stop identification, wayfinding and basic monitoring, including `ATCOCode`, `NaptanCode`, `CommonName`, `Street`, `Indicator`, `Bearing`, `LocalityName`, `Longitude`, `Latitude`, `BusStopType` and `TimingStatus`.

Area-level percentages are field-completeness rates, not route coverage or standard-compliance rates. `Street` means a stop record has a street-name field populated; it does not mean that percentage of streets has a bus route. `Longitude` and `Latitude` completeness means WGS84 coordinate fields are populated. The area summary also reports alternative grid-reference completeness where easting/northing-style fields are present, and an `any_location_reference` rate covering either WGS84 coordinates or a grid reference.

## Standard Readiness

The readiness matrix is a qualitative classification of whether current national open data can monitor selected features from Campaign for Better Transport's proposed National Bus Stop Standard.

The statuses are:

- `available`: the feature can be monitored directly from current national open data.
- `partial`: current national open data contains some related fields, but not enough to confirm physical provision.
- `not_available`: the feature is not consistently recorded in the national open dataset.

## Classification Rules

Records are treated as bus stop records where `StopType` starts with `BC`, which is the NaPTAN bus/coach stop family used in the source extract, or where `BusStopType` is populated. This keeps the filter transparent and testable while allowing for records where the bus stop type field carries the relevant bus-stop signal.

Readiness classifications are assigned from whether current national open data can monitor a proposed feature directly. Stop identity and location are `available`; stop-flag information is `partial` because NaPTAN records names and public codes but not physical sign content; facility and maintenance features are `not_available` because they are not consistently recorded in NaPTAN/NPTG.

## Validation

Validation checks that processed files and metadata exist, required columns are present, files are non-empty, percentages are between 0 and 100, area counts sum to the total number of filtered bus stop records, active area codes are matched to NPTG names, expected readiness features are present, quality-review prompts are recorded, and metadata paths and row counts match outputs.

## Limitations

NaPTAN does not include Northern Ireland. It is a transport reference dataset rather than an official statistics release.

The dataset cannot, on its own, confirm whether a stop has a shelter, seating, lighting, an up-to-date printed timetable, a route map, a QR code, a working real-time display, a cleaning programme or a repair contract. Those features would need to be collected through a local authority asset audit or a future national facility data standard.

## Suggested Future Audit Schema

A production monitor for a National Bus Stop Standard would need stop-level audit fields including:

- `atco_code`
- `audit_date`
- `auditing_body`
- `proposed_standard_category`
- `has_shelter`
- `has_seating`
- `has_printed_timetable`
- `has_route_map`
- `has_rti_display`
- `has_qr_or_weblink`
- `has_lighting`
- `has_accessible_boarding_area`
- `has_clear_stop_flag`
- `has_cleaning_programme`
- `has_repair_contract`
- `condition_rating`
- `evidence_url`
- `notes`
