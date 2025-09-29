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

.PHONY: publish
publish:
	./publish.sh

.PHONY: publish-single
publish-single:
	./publish-single.sh "$(FILE_PATH)"