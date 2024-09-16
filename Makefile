run-unit-tests:
	@echo "Running unit-tests.."
	PYTHONPATH=$(shell pwd) pytest -v

run-security-checks:
	@echo "Running security checks.."
	bandit app.py

run-black:
	@echo "Running black.."
	black --line-length=79 app.py

run-flake8:
	@echo "Running flake8.."
	flake8 app.py
