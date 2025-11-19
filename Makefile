# Makefile for the md2html Python project

# Shell to use
SHELL := /bin/bash

# Variables
PYTHON ?= python3
SRC_DIR := src
BUILD_DIR := build
DOCS_DIR := docs
USER_PYTHONPATH := $(PYTHONPATH)
LOCAL_PYTHONPATH := $(abspath $(SRC_DIR))

# Ensure Python picks up the in-repo package during development
export PYTHONPATH := $(LOCAL_PYTHONPATH)$(if $(strip $(USER_PYTHONPATH)),:$(USER_PYTHONPATH))

# Phony targets are not real files, they are recipes
.PHONY: help install test run run-hide watch serve clean
run-hide: ## Generate the static site, excluding ::: hide blocks
	@echo ">>> Generating site (excluding hide blocks) from '$(DOCS_DIR)' to '$(BUILD_DIR)/html'..."
	@$(PYTHON) -m md2html --src $(DOCS_DIR) --dst $(BUILD_DIR)/html --exclude-hide

# Default target executed when you just run `make`
.DEFAULT_GOAL := help

# Self-documenting targets
# The `##` is a convention for help text
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies for development
	@echo ">>> Installing dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]

test: ## Run unit tests with pytest
	@echo ">>> Running tests..."
	@$(PYTHON) -m pytest

run: ## Generate the static site from docs/ to build/html
	@echo ">>> Generating site from '$(DOCS_DIR)' to '$(BUILD_DIR)/html'..."
	@$(PYTHON) -m md2html --src $(DOCS_DIR) --dst $(BUILD_DIR)/html

watch: ## Run in watch mode to rebuild on changes
	@echo ">>> Starting watch mode... (Press Ctrl+C to exit)"
	@$(PYTHON) -m md2html --watch

serve: ## Serve with auto-reload after rebuilding on changes
	@echo ">>> Serving docs with live reload on http://127.0.0.1:8000 (Press Ctrl+C to exit)"
	@$(PYTHON) -m md2html.devserver --src $(DOCS_DIR) --dst $(BUILD_DIR)/html --host 127.0.0.1 --port 8000

serve-hide: ## Serve with auto-reload after rebuilding on changes
	@echo ">>> Serving docs with live reload on http://127.0.0.1:8000 (Press Ctrl+C to exit)"
	@$(PYTHON) -m md2html.devserver --src $(DOCS_DIR) --dst $(BUILD_DIR)/html --host 127.0.0.1 --port 8000 --exclude-hide

clean: ## Clean up build artifacts and Python cache files
	@echo ">>> Cleaning up..."
	@rm -rf $(BUILD_DIR) .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete

# Alias: build the static site (same as run)
build: run  ## Build the static site (alias for run)

.PHONY: docker docker-build docker-run docker-stop

docker: build docker-build docker-run

docker-build:
	docker build -t md2html-local-build .

docker-run:
	docker run --rm -d -p 8080:80 --name my-md-site-local md2html-local-build

docker-stop:
	docker stop my-md-site-local

