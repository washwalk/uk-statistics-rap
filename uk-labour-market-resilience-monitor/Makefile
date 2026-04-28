.PHONY: install fetch transform validate report test integration-test clean

install:
	python3 -m pip install -r requirements.txt

fetch:
	python3 src/fetch_ons.py

transform: fetch
	python3 src/transform.py

validate:
	python3 src/validate.py

report: integration-test
	python3 src/build_site.py

test: validate

integration-test: transform validate

clean:
	rm -f data/raw/*.json data/processed/*.csv data/processed/*.json
