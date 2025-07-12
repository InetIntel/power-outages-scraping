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
