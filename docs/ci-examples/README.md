# CI Examples

These are example GitHub Actions workflows for GSS RAP projects. They are provided as documented templates rather than active workflows so teams can adapt them before enabling automation.

Recommended use:

- copy the relevant example into `.github/workflows/`
- adjust Python, Quarto, dependency, and publication settings
- decide whether live source refresh and publication should be scheduled or manually approved

## Workflow Types

- `pull-request-offline-test.yml`: runs offline validation and tests on pull requests.
- `manual-live-integration-test.yml`: refreshes live source data and validates outputs on manual dispatch.
- `manual-build-and-publish.yml`: builds publication outputs after validation; publication deployment is left as a placeholder.

Keep `make test` offline. Put live source refreshes behind `make integration-test` or controlled scheduled/manual workflows.
