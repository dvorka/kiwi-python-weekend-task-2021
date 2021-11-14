# Kiwi.com Python weekend task '21: Martin Dvorak <martin.dvorak@mindforger.com>

.DEFAULT_GOAL := help

help:
	@echo "Help:"
	@echo "py-install	Python code style and test tools installation"
	@echo "lint   		format and lint"
	@echo "test   		run unit test(s)"

py-install:
	pip install black flake8 pytest

lint:
	black solution tests
	flake8 --max-line-length 88 solution tests

test:
	# pytest -s -vvv tests/test_kiwi.py
	pytest -s -vvv tests/test_kiwi.py::test_query
	# pytest -s -vvv tests/test_kiwi.py::test_result_serialization
