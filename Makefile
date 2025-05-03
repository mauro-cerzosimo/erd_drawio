.PHONY: watch lint format

watch:
	poetry run watchmedo shell-command \
		--patterns="*.dsl" \
		--recursive \
		--command='poetry run python run.py' \
		input/

lint:
	poetry run ruff check .

format:
	poetry run black .
