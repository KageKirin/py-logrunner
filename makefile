## Makefile for logrunner project

.PHONY: format
f format:
	ruff format src tests


.PHONY: lint
l lint:
	ruff check src tests


.PHONY: test
t test:
	uv run --with pytest pytest tests


.PHONY: pack
p pack:
	uv build

.PHONY: clean
c clean:
	uv clean
	rm -rf build dist *.egg-info __pycache__ src/**/__pycache__ tests/**/__pycache__

.PHONY: all
a all: c f l t p
