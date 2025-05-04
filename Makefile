.PHONY: watch lint format

watch:
	poetry run watchmedo shell-command \
		--patterns="*.dsl" \
		--recursive \
		--command='poetry run python run_generator.py' \
		input/
arrange:
	poetry run python run_table_locator.py

lint:
	poetry run ruff check .

format:
	poetry run black .

typecheck:
	poetry run mypy .
