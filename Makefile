.PHONY: deploy stop

deploy:
	docker compose up -d && ./publish.sh

stop:
	docker compose down
