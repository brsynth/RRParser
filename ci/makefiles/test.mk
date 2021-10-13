include ../.ci_env

SHELL := /bin/bash

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := all

MAKE_CMD = $(MAKE) -f test.mk -s --no-print-directory
ECHO = echo ">>>"

PACKAGE = $(shell python ../../setup.py --name)

ifeq ($(args),)
	test_src := tests
else
	test_src = $(args)
endif
test_cmd := python -m pytest -v --cov --cov-report term-missing
define test_deps
    - pytest
    - pytest-cov
    - pytest-mock
endef
export test_deps

test-cmd:
	@echo $(test_cmd)
test-deps:
	@echo "$$test_deps"

all: check test ## Run check and test code

# CHECK
check: flake bandit ## Run flake and bandit over code and tests
bandit: ## Run bandit over code
	@echo "=== BANDIT REPORT ==="
	# -lll to only catch the higher level security issues
	@bandit -r -lll ../../${PACKAGE}
flake: ## Run flake over code and tests
	echo "=== FLAKE REPORT ==="
	# stop the build if there are Python syntax errors or undefined names
	flake8 ../../${PACKAGE} --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 ../../${PACKAGE} --count --ignore=E272,E501,E266,E241,E226,E251,E303,E221 --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 ../../$(test_src) --count --ignore=E272,E501,E266,E241,E226,E251,E303,E221,E122,E211,E302 --exit-zero --max-complexity=10 --max-line-length=127 --statistics


# TEST
test: ## Test code with 'pytest'
	@export PYTHONPATH=$$PWD/../.. ; \
	cd ../.. ; \
	$(test_cmd) -p no:cacheprovider $(test_src) ; \
	res_test=$$? ; \
	if [ $$res_test -eq 0 ] || [ $$res_test -eq 5 ] ; then \
		exit 0 ; \
	fi

