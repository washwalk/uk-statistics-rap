.PHONY: install fetch transform validate test integration-test report clean

install:
	python3 -m pip install -r requirements.txt

fetch:
	python3 src/fetch.py

transform:
	python3 src/transform.py

validate:
	python3 src/validate.py

test:
	python3 -m unittest discover -s tests
	$(MAKE) validate

integration-test: fetch transform validate

report: integration-test
	python3 src/publish.py

clean:
	rm -f data/raw/source.csv data/raw/nptg.xml data/raw/source-metadata.json data/processed/area-summary.csv data/processed/completeness-summary.csv data/processed/data-dictionary.csv data/processed/standard-readiness.csv data/processed/run-metadata.json docs/index.html docs/data/area-summary.csv docs/data/completeness-summary.csv docs/data/data-dictionary.csv docs/data/standard-readiness.csv docs/data/run-metadata.json
