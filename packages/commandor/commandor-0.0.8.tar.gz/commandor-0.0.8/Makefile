all: clean-pyc test

test:
	python setup.py nosetests --stop --tests tests/__init__.py

travis:
	python setup.py nosetests --tests tests/__init__.py

coverage:
	python setup.py nosetests  --with-coverage --cover-package=commandor --cover-html --cover-html-dir=coverage_out coverage


shell:
	../venv/bin/ipython

audit:
	python setup.py autdit

release: clean
	python setup.py sdist upload

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean: clean-pyc
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.egg-info' -exec rm -rf {} +

find-print:
	grep -r --include=*.py --exclude-dir=venv --exclude=fabfile* --exclude=tests.py --exclude-dir=tests --exclude-dir=commands 'print' ./