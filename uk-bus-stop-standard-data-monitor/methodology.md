# Methodology

## Source

The pipeline uses the Department for Transport National Public Transport Access Nodes (NaPTAN) API. NaPTAN is the national register of public transport access points in England, Scotland and Wales.

The configured source is `https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv`.

## Processing

The live CSV is stored unchanged in `data/raw/source.csv`. The transform step reads the CSV and filters to bus-related records where `StopType` begins with `BC` or `BusStopType` is populated.

The pipeline then produces three processed outputs:

- `area-summary.csv`: stop counts and selected completeness rates by administrative area code.
- `completeness-summary.csv`: national completeness rates for fields that support passenger information and monitoring.
- `standard-readiness.csv`: a matrix mapping proposed National Bus Stop Standard features to current national open-data availability.

## Completeness Measures

Completeness is calculated as the share of filtered bus stop records where a field is non-blank. The monitor focuses on fields relevant to stop identification, wayfinding and basic monitoring, including `ATCOCode`, `NaptanCode`, `CommonName`, `Street`, `Indicator`, `Bearing`, `LocalityName`, `Longitude`, `Latitude`, `BusStopType` and `TimingStatus`.

## Standard Readiness

The readiness matrix is a qualitative classification of whether current national open data can monitor selected features from Campaign for Better Transport's proposed National Bus Stop Standard.

The statuses are:

- `available`: the feature can be monitored directly from current national open data.
- `partial`: current national open data contains some related fields, but not enough to confirm physical provision.
- `not_available`: the feature is not consistently recorded in the national open dataset.

## Validation

Validation checks that processed files and metadata exist, required columns are present, files are non-empty, percentages are between 0 and 100, area counts sum to the total number of filtered bus stop records, expected readiness features are present, and metadata paths and row counts match outputs.

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
