IMAGE_NAME={{cookiecutter.project_slug}}:latest


.PHONY: build
build:
	@echo "Build docker image..."
	docker build --build-arg MODE=dev -t $(IMAGE_NAME) .

.PHONY: up
up:
	docker compose up -d


.PHONY: down
down:
	docker compose down --remove-orphans


.PHONY: unit-test
unit-test:
	@echo "Running unit tests..."
	@make up
	docker exec -it app pytest -v -s -p no:warnings
	@make down


.PHONY: ci-test
ci-test:
	@echo "Running CI tests..."
	act -j test


.PHONY: init
init:
	@echo "Running init project"
	bash scripts/init.sh
