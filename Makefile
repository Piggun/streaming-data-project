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

zip-lambda:
	mkdir my_lambda_project && cd my_lambda_project &&\
	pip install --target ./package boto3 requests python-dotenv && cd package &&\
	zip -r ../lambda_function.zip . && cd .. &&\
	zip -g lambda_function.zip ../app.py
