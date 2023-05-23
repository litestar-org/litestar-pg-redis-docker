.PHONY: all clean lint test

all: lint test

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .tox .ruff_cache

lint:
	poetry run ruff app tests
	poetry run mypy app tests
	# poetry run pyright app
	# poetry run pre-commit run --all-files

test:
	poetry run pytest
