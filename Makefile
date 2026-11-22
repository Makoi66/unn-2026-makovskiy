.PHONY: install test check ruff-cs-check ruff-cs-fix ruff-linter-check ruff-linter-fix mypy-check build run

IMAGE = echo-bot

install:
	uv sync --locked --group dev

test:
	uv run python -m unittest discover -s tests -v

check: ruff-cs-check ruff-linter-check mypy-check test

ruff-cs-check:
	uv run ruff format --check .

ruff-cs-fix:
	uv run ruff format .

ruff-linter-check:
	uv run ruff check .

ruff-linter-fix:
	uv run ruff check --fix .

mypy-check:
	uv run mypy

build:
	docker build -t $(IMAGE) .

run: build
	docker run --rm --env-file .env $(IMAGE)
