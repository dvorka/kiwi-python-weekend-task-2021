# Kiwi.com Python weekend task '21: Martin Dvorak <martin.dvorak@mindforger.com>

.DEFAULT_GOAL := help

help:
	@echo "Help:"
	@echo "py-install	Python code style and test tools installation"
	@echo "lint   		format and lint"
	@echo "test   		run unit test(s)"
	@echo "example		run flight search example using solution"

py-install:
	pip install black flake8 pytest

lint:
	black solution.py tests
	flake8 --max-line-length 88 solution.py tests

test:
	pytest tests/test_kiwi.py
	# pytest -s -vvv tests/test_kiwi.py
	# pytest -s -vvv tests/test_kiwi.py::test_query
	# pytest -s -vvv tests/test_kiwi.py::test_result_serialization
	# pytest -s -vvv tests/test_kiwi.py::test_max_stops
	# pytest -s -vvv tests/test_kiwi.py::test_max_price

example:
	# python -m solution -h
	python -m solution datasets/example0.csv RFZ WIW --bags=1 --return
	# python -m solution datasets/example3.csv WUE NNB --bags=1 --max_price 75
	# python -m solution datasets/example3.csv VVH ZRW --bags=1 --max_stops 2
