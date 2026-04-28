.PHONY: install validate test integration-test build build-labour-market build-retail-sales build-housing clean

install:
	$(MAKE) -C uk-labour-market-resilience-monitor install
	$(MAKE) -C ons-retail-sales-rap install
	$(MAKE) -C uk-housing-affordability-monitor install

validate:
	$(MAKE) -C uk-labour-market-resilience-monitor validate
	$(MAKE) -C ons-retail-sales-rap validate
	$(MAKE) -C uk-housing-affordability-monitor validate

test:
	$(MAKE) -C uk-labour-market-resilience-monitor test
	$(MAKE) -C ons-retail-sales-rap test
	$(MAKE) -C uk-housing-affordability-monitor test

integration-test:
	$(MAKE) -C uk-labour-market-resilience-monitor integration-test
	$(MAKE) -C ons-retail-sales-rap integration-test
	$(MAKE) -C uk-housing-affordability-monitor integration-test

build: build-labour-market build-retail-sales build-housing

build-labour-market:
	$(MAKE) -C uk-labour-market-resilience-monitor report

build-retail-sales:
	$(MAKE) -C ons-retail-sales-rap report

build-housing:
	$(MAKE) -C uk-housing-affordability-monitor report

clean:
	$(MAKE) -C uk-labour-market-resilience-monitor clean
	$(MAKE) -C ons-retail-sales-rap clean
	$(MAKE) -C uk-housing-affordability-monitor clean
