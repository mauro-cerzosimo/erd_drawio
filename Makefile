.PHONY: watch drawio arrange lint format typecheck

# Watch for changes in input/ and output/ using watcher.py
watch:
	poetry run python watcher.py

# Run the Draw.io generator script manually
drawio:
	poetry run python run_generator.py

# Run the table locator script manually
arrange:
	poetry run python run_table_locator.py

# Run ruff linter
lint:
	poetry run ruff check .

# Run black code formatter
format:
	poetry run black .

# Run mypy type checking
typecheck:
	poetry run mypy .
