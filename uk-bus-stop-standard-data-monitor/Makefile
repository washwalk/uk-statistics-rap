.DELETE_ON_ERROR:

PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,$(if $(wildcard .venv/bin/python),.venv/bin/python,python3))

.PHONY: install fetch fetch-bods transform validate test integration-test report report-live report-offline clean

install:
	$(PYTHON) -m pip install -r requirements.txt

fetch:
	$(PYTHON) src/fetch.py

fetch-bods:
	$(PYTHON) src/fetch_bods.py

transform:
	$(PYTHON) src/transform.py

validate:
	$(PYTHON) src/validate.py

test:
	$(PYTHON) -m unittest discover -s tests
	$(MAKE) validate

integration-test: fetch transform validate

report: report-live

report-live: integration-test
	$(PYTHON) src/publish.py

report-offline: transform validate
	$(PYTHON) src/publish.py

clean:
	rm -f data/raw/source.csv data/raw/nptg.xml data/raw/source-metadata.json data/raw/bods-timetables.json data/raw/bods-location-feeds.json data/raw/bods-fares.json data/raw/bods-source-metadata.json data/processed/area-summary.csv data/processed/bods-summary.csv data/processed/bods-area-summary.csv data/processed/completeness-summary.csv data/processed/data-dictionary.csv data/processed/standard-readiness.csv data/processed/audit-requirements.csv data/processed/run-metadata.json data/processed/validation-results.json examples/example-stop-audit.csv docs/index.html docs/data/area-summary.csv docs/data/bods-summary.csv docs/data/bods-area-summary.csv docs/data/completeness-summary.csv docs/data/data-dictionary.csv docs/data/standard-readiness.csv docs/data/audit-requirements.csv docs/data/example-stop-audit.csv docs/data/run-metadata.json docs/data/validation-results.json
