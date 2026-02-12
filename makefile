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

.PHONY: all
a all: f l t p
