all: install test

install:
	python setup.py install

test: deps
	specloud tests

deps:
	pip install -r requirements-dev.txt
