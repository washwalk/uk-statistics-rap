.PHONY: install pipeline report test clean

install:
	python3 -m pip install -r requirements.txt

pipeline:
	python3 -m src.pipeline

report: pipeline
	quarto render reports/statistical_summary.qmd --output-dir ../outputs

test:
	python3 -m pytest

clean:
	rm -f data/raw/*.csv data/raw/*.json data/processed/*.csv outputs/figures/*.png outputs/tables/*.csv outputs/*.html
