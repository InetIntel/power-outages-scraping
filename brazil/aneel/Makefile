.PHONY: run
run: stop
	docker compose up -d

.PHONY: stop
stop:
	docker compose down

.PHONY: build
build:
	docker build -t localhost:5000/brazil-aneel-scraper:latest .

.PHONY: publish
publish: build
	docker push localhost:5000/brazil-aneel-scraper:latest
