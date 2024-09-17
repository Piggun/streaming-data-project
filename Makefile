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
	pip install --target ./package -r ../main-requirements.txt && cd package &&\
	zip -r ../lambda_function.zip . && cd .. &&\
	zip -g lambda_function.zip ../app.py

create-environment:
	python -m venv venv
	@echo "\nVirtual environment has been created, \
	run the following command to activate it:\n\n\
	source venv/bin/activate"

install-dependencies:
	pip install -r ./requirements.txt