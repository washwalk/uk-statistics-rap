.PHONY: install validate test integration-test build build-labour-market build-retail-sales build-housing build-inflation build-gdp build-population build-bus-stop-standard clean

install:
	$(MAKE) -C uk-labour-market-resilience-monitor install
	$(MAKE) -C ons-retail-sales-rap install
	$(MAKE) -C uk-housing-affordability-monitor install
	$(MAKE) -C uk-inflation-monitor install
	$(MAKE) -C uk-gdp-release-summary install
	$(MAKE) -C uk-population-change-explorer install
	$(MAKE) -C uk-bus-stop-standard-data-monitor install

validate:
	$(MAKE) -C uk-labour-market-resilience-monitor validate
	$(MAKE) -C ons-retail-sales-rap validate
	$(MAKE) -C uk-housing-affordability-monitor validate
	$(MAKE) -C uk-inflation-monitor validate
	$(MAKE) -C uk-gdp-release-summary validate
	$(MAKE) -C uk-population-change-explorer validate
	$(MAKE) -C uk-bus-stop-standard-data-monitor validate

test:
	$(MAKE) -C uk-labour-market-resilience-monitor test
	$(MAKE) -C ons-retail-sales-rap test
	$(MAKE) -C uk-housing-affordability-monitor test
	$(MAKE) -C uk-inflation-monitor test
	$(MAKE) -C uk-gdp-release-summary test
	$(MAKE) -C uk-population-change-explorer test
	$(MAKE) -C uk-bus-stop-standard-data-monitor test

integration-test:
	$(MAKE) -C uk-labour-market-resilience-monitor integration-test
	$(MAKE) -C ons-retail-sales-rap integration-test
	$(MAKE) -C uk-housing-affordability-monitor integration-test
	$(MAKE) -C uk-inflation-monitor integration-test
	$(MAKE) -C uk-gdp-release-summary integration-test
	$(MAKE) -C uk-population-change-explorer integration-test
	$(MAKE) -C uk-bus-stop-standard-data-monitor integration-test

build: build-labour-market build-retail-sales build-housing build-inflation build-gdp build-population build-bus-stop-standard

build-labour-market:
	$(MAKE) -C uk-labour-market-resilience-monitor report

build-retail-sales:
	$(MAKE) -C ons-retail-sales-rap report

build-housing:
	$(MAKE) -C uk-housing-affordability-monitor report

build-inflation:
	$(MAKE) -C uk-inflation-monitor report

build-gdp:
	$(MAKE) -C uk-gdp-release-summary report

build-population:
	$(MAKE) -C uk-population-change-explorer report

build-bus-stop-standard:
	$(MAKE) -C uk-bus-stop-standard-data-monitor report

clean:
	$(MAKE) -C uk-labour-market-resilience-monitor clean
	$(MAKE) -C ons-retail-sales-rap clean
	$(MAKE) -C uk-housing-affordability-monitor clean
	$(MAKE) -C uk-inflation-monitor clean
	$(MAKE) -C uk-gdp-release-summary clean
	$(MAKE) -C uk-population-change-explorer clean
	$(MAKE) -C uk-bus-stop-standard-data-monitor clean
