.PHONY: install fetch transform validate report test integration-test clean

install:
	python3 -m pip install -r requirements.txt

fetch:
	python3 scripts/fetch_ons_data.py

transform: fetch

validate:
	python3 scripts/validate_outputs.py

report: integration-test
	quarto render

test: validate

integration-test: transform validate

clean:
	rm -rf _site
