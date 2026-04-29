.DELETE_ON_ERROR:

PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,$(if $(wildcard .venv/bin/python),.venv/bin/python,python3))

.PHONY: install fetch transform validate pipeline report report-live report-offline test integration-test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

fetch:
	$(PYTHON) -m src.pipeline

transform: fetch

validate:
	$(PYTHON) scripts/validate_outputs.py

pipeline:
	$(PYTHON) -m src.pipeline

report: report-live

report-live: integration-test
	quarto render reports/statistical_summary.qmd --output-dir ../outputs

report-offline: transform validate
	quarto render reports/statistical_summary.qmd --output-dir ../outputs

test: validate
	$(PYTHON) -m pytest

integration-test: pipeline validate

clean:
	rm -f data/raw/*.csv data/raw/*.json data/processed/*.csv outputs/figures/*.png outputs/tables/*.csv outputs/*.html
