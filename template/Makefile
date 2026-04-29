.DELETE_ON_ERROR:

PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,$(if $(wildcard .venv/bin/python),.venv/bin/python,python3))

.PHONY: install fetch transform validate test integration-test report report-live report-offline clean

install:
	$(PYTHON) -m pip install -r requirements.txt

fetch:
	$(PYTHON) src/fetch.py

transform:
	$(PYTHON) src/transform.py

validate:
	$(PYTHON) src/validate.py

test: validate
	$(PYTHON) -m pytest

integration-test: fetch transform validate

report: report-live

report-live: integration-test
	$(PYTHON) src/publish.py

report-offline: transform validate
	$(PYTHON) src/publish.py

clean:
	rm -f data/raw/* data/processed/* outputs/figures/* outputs/tables/* outputs/*.html
