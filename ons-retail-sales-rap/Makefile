.PHONY: install fetch transform validate pipeline report test integration-test clean

install:
	python3 -m pip install -r requirements.txt

fetch:
	python3 -m src.pipeline

transform: fetch

validate:
	python3 scripts/validate_outputs.py

pipeline:
	python3 -m src.pipeline

report: integration-test
	quarto render reports/statistical_summary.qmd --output-dir ../outputs

test: validate
	python3 -m pytest

integration-test: pipeline validate

clean:
	rm -f data/raw/*.csv data/raw/*.json data/processed/*.csv outputs/figures/*.png outputs/tables/*.csv outputs/*.html
