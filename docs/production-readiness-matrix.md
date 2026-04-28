# Production Readiness Matrix

Use this matrix to separate what the examples demonstrate from the controls a team would still need before using the pattern for a live official-statistics output.

Statuses:

- `Demonstrated`: implemented directly in the example.
- `Partial`: present as a lightweight example or documented pattern, but not production-complete.
- `Not in scope`: deliberately not implemented in these compact examples.

| Control area | Labour market | Retail sales | Housing affordability | Template | Production expectation |
| --- | --- | --- | --- | --- | --- |
| Source provenance | Demonstrated | Demonstrated | Demonstrated | Partial | Source URLs, dataset IDs, release dates, and licence terms are recorded and reviewable. |
| Reproducible command interface | Demonstrated | Demonstrated | Demonstrated | Demonstrated | Analysts and CI can run install, validation, integration, and publication commands consistently. |
| Raw and processed separation | Demonstrated | Demonstrated | Partial | Demonstrated | Raw extracts, processed data, and publication outputs are separated and documented. |
| Offline validation | Demonstrated | Demonstrated | Demonstrated | Demonstrated | `make test` runs without source API calls and fails clearly when existing outputs are invalid. |
| Live source integration check | Demonstrated | Demonstrated | Demonstrated | Demonstrated | `make integration-test` refreshes live source data and validates the result. |
| Unit tests for statistical logic | Not in scope | Demonstrated | Not in scope | Partial | Publication-critical calculations have targeted unit tests. |
| Run metadata | Demonstrated | Demonstrated | Demonstrated | Demonstrated | Each run writes source, timestamp, row count, output, and validation metadata. |
| Revision monitoring | Not in scope | Not in scope | Not in scope | Not in scope | Teams define checks for source revisions and unexpected movement in headline statistics. |
| Accessibility checks | Partial | Partial | Partial | Not in scope | HTML outputs are checked for headings, contrast, keyboard use, text alternatives, and mobile behaviour. |
| Disclosure control | Not in scope | Not in scope | Not in scope | Not in scope | Required only where source/output risk requires it; teams document the assessment. |
| Dependency management | Partial | Partial | Partial | Partial | Dependencies are pinned or otherwise controlled according to departmental policy. |
| CI automation | Partial | Partial | Partial | Partial | Pull request checks, scheduled integration checks, and controlled publication jobs are configured. |
| Peer review and sign-off | Not in scope | Not in scope | Not in scope | Not in scope | Statistical, code, accessibility, and release sign-off happen outside the example code. |
| Incident and failure process | Not in scope | Not in scope | Not in scope | Not in scope | Teams know what happens when source data, validation, or publication fails. |

## How To Use The Matrix

1. Start from the `template/` folder or the closest worked example.
2. Copy the relevant demonstrated controls into your project.
3. Mark any partial controls that need strengthening for your output.
4. Record controls that are not applicable, such as disclosure control for fully aggregate open data.
5. Do not treat a passing pipeline as publication sign-off; it is evidence for review, not a replacement for review.

## Minimum Production Consideration Gate

Before a RAP is considered ready for production assessment, it should normally have:

- documented source provenance and licensing
- a reproducible command path from source to output
- automated validation for schema, grain, missingness, duplicates, and plausible values
- tests for publication-critical statistical logic
- run metadata for audit and release comparison
- documented limitations, quality notes, and methodology
- agreed ownership, review, and release sign-off
