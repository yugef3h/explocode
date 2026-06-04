.PHONY: install test lint run

install:
	python3 -m venv .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check manus_agent tests

run:
	.venv/bin/manus run "Write a brief multi-agent architecture report"
