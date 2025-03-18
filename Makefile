reqs: 
	pip install --upgrade pip && \
	pip install pip-tools && \
	pip-compile requirements.in && \
	pip-compile requirements_test.in && \
	pip-compile requirements_dev.in

sync: reqs
	pip-sync requirements.txt requirements_test.txt requirements_dev.txt

install: reqs
	pip install -r requirements.txt -r requirements_dev.txt -r requirements_test.txt

lint: 
	echo "mypy" 
	python3 -m mypy --explicit-package-bases .
	echo "black" 
	python3 -m black . 
	echo "ruff" 
	ruff check . 
	echo "safety"
	safety check -r requirements.txt

tests: 
	echo "calling pytest tests"
	python3 -m pytest tests/unit/ tests/functional/ tests/integration/

all: reqs install lint tests