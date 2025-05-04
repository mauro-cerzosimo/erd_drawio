.PHONY: watch lint format

watch:
	poetry run python watcher.py

drawio:
  	poetry run python run_generator.py
		
arrange:
	poetry run python run_table_locator.py

lint:
	poetry run ruff check .

format:
	poetry run black .

typecheck:
	poetry run mypy .
