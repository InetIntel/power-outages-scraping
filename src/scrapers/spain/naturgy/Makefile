.PHONY: build
build:
	docker build -t localhost:5000/spain-naturgy-scraper:latest .

.PHONY: publish
publish: build
	docker push localhost:5000/spain-naturgy-scraper:latest
