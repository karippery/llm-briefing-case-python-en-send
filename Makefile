.PHONY: install run test lint typecheck

install:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy app
