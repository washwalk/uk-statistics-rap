.PHONY: install fetch transform validate test integration-test report clean

install:
	python3 -m pip install -r requirements.txt

fetch:
	python3 src/fetch.py

transform:
	python3 src/transform.py

validate:
	python3 src/validate.py

test: validate
	python3 -m pytest

integration-test: fetch transform validate

report: integration-test
	python3 src/publish.py

clean:
	rm -f data/raw/* data/processed/* outputs/figures/* outputs/tables/* outputs/*.html
