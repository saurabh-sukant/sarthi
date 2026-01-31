.PHONY: help build build-nocache up down logs clean restart rebuild stop ps shell test push init-env

# Environment file
ENV_FILE := .env
ENV_EXAMPLE := .env.example

# Default target
help:
	@echo "Sarthi Docker & Docker Compose Commands"
	@echo "========================================"
	@echo "build              - Build Docker image"
	@echo "build-nocache      - Build Docker image without cache"
	@echo "up                 - Start Docker Compose services"
	@echo "down               - Stop Docker Compose services"
	@echo "logs               - View Docker Compose logs"
	@echo "logs-api           - View sarthi-api logs"
	@echo "logs-chroma        - View chroma-db logs"
	@echo "clean              - Remove containers, volumes, and images"
	@echo "restart            - Restart all services"
	@echo "rebuild            - Rebuild and restart services"
	@echo "stop               - Stop all services (keep containers)"
	@echo "ps                 - Show running containers"
	@echo "shell              - Open shell in sarthi-api container"
	@echo "test               - Run tests in container"
	@echo "push               - Push Docker image to registry (requires IMAGE_NAME)"
	@echo "init-env           - Initialize environment variables"

# Initialize environment variables
init-env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Creating $(ENV_FILE)..."; \
		echo "OPENAI_API_KEY=" > $(ENV_FILE); \
		echo "SECRET_KEY=" >> $(ENV_FILE); \
		echo "DATABASE_URL=sqlite:///./sarthi.db" >> $(ENV_FILE); \
		echo "CHROMA_PATH=./chroma_db" >> $(ENV_FILE); \
	fi
	@echo "✓ Environment file initialized: $(ENV_FILE)"
	@echo "Please update the following variables in $(ENV_FILE):"
	@echo "  - OPENAI_API_KEY"
	@echo "  - SECRET_KEY"

# Build Docker image
build: init-env
	docker build -t sarthi:latest .

# Build Docker image without cache
build-nocache: init-env
	docker build --no-cache -t sarthi:latest .

# Start Docker Compose services
up: init-env
	docker-compose up -d

# Stop Docker Compose services and remove containers
down:
	docker-compose down

# View logs from all services
logs:
	docker-compose logs -f

# View logs from sarthi-api service
logs-api:
	docker-compose logs -f sarthi-api

# View logs from chroma-db service
logs-chroma:
	docker-compose logs -f chroma-db

# Remove containers, volumes, and images
clean:
	docker-compose down -v
	docker rmi sarthi:latest 2>/dev/null || true

# Restart all services
restart: down up
	@echo "Services restarted"

# Rebuild image and restart services
rebuild: clean build up
	@echo "Services rebuilt and restarted"

# Stop services without removing containers
stop:
	docker-compose stop

# Show running containers
ps:
	docker-compose ps

# Open shell in running sarthi-api container
shell:
	docker-compose exec sarthi-api /bin/bash

# Run tests in the container
test:
	docker-compose exec sarthi-api python -m pytest

# Build and up in one command
start: build up

# Status check
status:
	@echo "Docker Compose Status:"
	@docker-compose ps
	@echo "\nDocker Images:"
	@docker images | grep sarthi

# Push image to registry (usage: make push IMAGE_NAME=your-registry/sarthi:latest)
push:
	@if [ -z "$(IMAGE_NAME)" ]; then \
		echo "Error: IMAGE_NAME not specified. Usage: make push IMAGE_NAME=your-registry/sarthi:latest"; \
		exit 1; \
	fi
	docker tag sarthi:latest $(IMAGE_NAME)
	docker push $(IMAGE_NAME)

# Validate docker-compose configuration
validate:
	docker-compose config

# Show help (default)
.DEFAULT_GOAL := help
