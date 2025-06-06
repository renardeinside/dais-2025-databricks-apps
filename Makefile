run-app:
	streamlit run src/dais_2025_databricks_apps/app.py

fmt:
	uv run black .
	uv run ruff check . --fix

lint:
	uv run black . --check
	uv run ruff check .