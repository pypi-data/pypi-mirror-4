init:
	pip install -r requirements.txt

start-debug: server
	python -m womack.server --debug

start: server
	python -m womack.server

server:
	pip install -r requirements-server.txt

dev:
	pip install -r requirements-test.txt
	pip install -r requirements-docs.txt

test:
	tox

functional-test:
	tox -e func

docs: dev
	pip install -r requirements-docs.txt
	cd docs; $(MAKE) html

tox: dev

.PHONY: tox docs
