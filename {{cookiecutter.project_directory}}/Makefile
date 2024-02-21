IMAGE_NAME=fastapi-templates:latest

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




define copy_file_if_not_exist
if [ ! -f $(2) ]; then \
  cp $(1) $(2); \
  echo "File $(2) has been created from $(1)"; \
else \
  echo "File $(2) already exists, skipping copy."; \
fi
endef

.PHONY: init
init:
	$(call copy_file_if_not_exist,example.env,.env)
