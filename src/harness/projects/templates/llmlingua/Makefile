.PHONY: install style test

PYTHON ?= python
CHECK_DIRS := base datasets models tasks tests

install:
	@${PYTHON} -m pip install .

style:
	black $(CHECK_DIRS)
	isort $(CHECK_DIRS)
	flake8 $(CHECK_DIRS)

test:
	@${PYTHON} -m pytest -n auto --dist=loadfile -s -v ./tests/
