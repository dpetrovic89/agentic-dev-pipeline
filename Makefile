install:
	pip install -e ".[dev]"

run:
	python -m pipeline.graph.pipeline_graph --spec SPEC.md

test:
	pytest tests/ --cov=pipeline --cov-report=term-missing

lint:
	ruff check pipeline/ tests/

# Determine OS for cleanup
ifeq ($(OS),Windows_NT)
    CLEAN_CMD = if exist .pytest_cache (rd /s /q .pytest_cache) & if exist .coverage (del .coverage) & if exist logs (del /q logs\*)
else
    CLEAN_CMD = rm -rf .pytest_cache .coverage logs/*
endif

clean:
	$(CLEAN_CMD)
