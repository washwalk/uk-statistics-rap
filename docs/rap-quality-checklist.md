# RAP Quality Checklist For GSS Outputs

Use this checklist when developing or reviewing a reproducible analytical pipeline for a statistical output. It is written for practical GSS use and should be adapted to the risk, profile, and publication status of the output.

## Source Data

- Source datasets, API endpoints, and download URLs are documented.
- Dataset versions, release dates, or metadata endpoints are captured where available.
- Raw data or raw metadata are retained long enough to support audit and reruns.
- Licensing and attribution are documented.
- Known source limitations, revisions policies, and coverage constraints are included in the methodology.

## Reproducibility

- The pipeline can be run from a clean checkout using documented commands.
- Raw, processed, and publication outputs are stored in separate locations.
- Generated files are either reproducible from code or explicitly versioned when there is a reason to retain them.
- Dependencies are documented and suitable for the intended use.
- The workflow avoids manual editing between data ingestion and final output.

## Data Processing

- Filters and transformations are documented in plain language.
- Code uses stable identifiers where possible, such as dataset IDs, geography codes, or series IDs.
- Joins are checked for unexpected unmatched records, duplicates, and many-to-many relationships.
- Date parsing, period ordering, and latest-period selection are tested or validated.
- Derived indicators are defined with clear formulas and units.

## Automated Quality Assurance

- Validation checks run before publication.
- Required columns, data types, row counts, and non-empty outputs are checked.
- Missing values, duplicate keys, invalid dates, and impossible values are flagged.
- Large revisions or unexpected changes from the previous run are reviewed where relevant.
- Tests cover the most important transformation logic and publication-critical calculations.

## Assurance Coverage In These Examples

| Assurance feature | Labour market | Retail sales | Housing affordability |
| --- | --- | --- | --- |
| Offline `make test` | Existing-output validation | Existing-output validation and unit tests | Existing-output validation |
| Live `make integration-test` | Fetch, transform, validate | Fetch/transform pipeline, validate | Fetch/transform pipeline, validate |
| Required file checks | Yes | Yes | Yes |
| Required column checks | Yes | Yes | Yes |
| Numeric plausibility checks | Yes | Yes | Yes |
| Duplicate key checks | Indicator-period | Period | Area-year |
| Run metadata | Yes | Yes | Yes |
| Conventional unit tests | Not yet | Yes | Not yet |
| Automated accessibility checks | Not yet | Not yet | Not yet |
| Revisions tracking | Not yet | Not yet | Not yet |

For a fuller view of what is demonstrated, partial, or out of scope, see [`production-readiness-matrix.md`](production-readiness-matrix.md).

## Statistical Communication

- The output explains what the statistics show and what they do not show.
- Caveats are close to the relevant statistics, not hidden in code or a separate document only.
- Uncertainty, confidence intervals, quality flags, or source-quality notes are included where available.
- Commentary distinguishes clearly between descriptive statistics, interpretation, and any judgement.
- The output links back to source publications and methodology.

## Accessibility And Publication

- Pages use meaningful headings, link text, titles, and table captions.
- Charts have text alternatives or accompanying data tables.
- Colour is not the only way information is communicated.
- Keyboard navigation, focus states, and contrast are checked.
- HTML outputs are reviewed on mobile and desktop screen sizes.

## Governance And Audit

- The repository has clear ownership and contact routes.
- Reviewers can see what changed between releases through version control or run metadata.
- Scheduled workflows, manual triggers, and failure notifications are understood by the team.
- Publication sign-off is separate from technical automation where required.
- Sensitive data, credentials, and unpublished statistics are not committed to the repository.

## Code Of Practice Alignment

- Trustworthiness: roles, review, release process, and audit trail are clear.
- Quality: source suitability, methods, validation, and limitations are documented.
- Value: outputs answer a user need and communicate findings accessibly.
