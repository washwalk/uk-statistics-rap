.DELETE_ON_ERROR:

PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,$(if $(wildcard .venv/bin/python),.venv/bin/python,python3))

.PHONY: install fetch transform validate report report-live report-offline test integration-test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

fetch:
	$(PYTHON) scripts/fetch_ons_data.py

transform: fetch

validate:
	$(PYTHON) scripts/validate_outputs.py

report: report-live

report-live: integration-test
	quarto render

report-offline: transform validate
	quarto render

test: validate

integration-test: transform validate

clean:
	rm -rf _site
