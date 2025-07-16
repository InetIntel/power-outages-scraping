.PHONY: docker-local-setup
docker-local-setup:
	mkdir registry_data
	mkdir minio_data
	mkdir dagu_config

.PHONY: run
run: stop
	docker compose up -d

.PHONY: stop
stop:
	docker compose down

.PHONY: build
build:
	docker build -t localhost:5000/brazil-aneel-scraper:latest -f ./brazil/aneel/Dockerfile .

.PHONY: publish
publish: build
	docker push localhost:5000/brazil-aneel-scraper:latest

