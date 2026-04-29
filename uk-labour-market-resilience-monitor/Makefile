.DELETE_ON_ERROR:

PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,$(if $(wildcard .venv/bin/python),.venv/bin/python,python3))

.PHONY: install fetch transform validate report report-live report-offline test integration-test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

fetch:
	$(PYTHON) src/fetch_ons.py

transform: fetch
	$(PYTHON) src/transform.py

validate:
	$(PYTHON) src/validate.py

report: report-live

report-live: integration-test
	$(PYTHON) src/build_site.py

report-offline: transform validate
	$(PYTHON) src/build_site.py

test: validate

integration-test: transform validate

clean:
	rm -f data/raw/*.json data/processed/*.csv data/processed/*.json
