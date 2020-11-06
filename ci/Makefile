SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

include $(SELF_DIR)/.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help: ## Basic help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := all

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

MAKE_CMD = $(MAKE) -s -C makefiles

# PYTHON VERSION
ifneq ($(strip $(python)),)
	PYTHON = python=$(python)
	PYTHON_ENV = _python$(python)
endif
ifeq ($(env),)
	env = build
endif


all: build test convert publish ## (default) Perform all conda process (build, test, convert, publish)

clean:
	@$(MAKE_CMD) -f conda-tools.mk clean

# CONDA WORKFLOW
build: ## Build (without tests) conda package, if 'python=<version>' cli argument is passed, python=<version> will be installed within the environment
	@$(MAKE_CMD) -f conda-tools.mk conda-build-only$(PYTHON_ENV)

check: ## Test conda package, if 'python=<version>' cli argument is passed, python=<version> will be installed within the environment
	@$(MAKE) check-environment-check env=check
	@$(MAKE_CMD) -f conda-env.mk conda-run-env env=check cmd="make -f test.mk check"

test: ## Test conda package, if 'python=<version>' cli argument is passed, python=<version> will be installed within the environment
	@$(MAKE_CMD) -f conda-tools.mk conda-test-only$(PYTHON_ENV)

convert: ## Convert conda package towards all platforms, if 'python=<version>' cli argument is passed, python=<version> will be installed within the environment
	@$(MAKE_CMD) -f conda-tools.mk conda-convert$(PYTHON_ENV)

publish: ## Publish conda package, if 'python=<version>' cli argument is passed, python=<version> will be installed within the environment
	@$(MAKE_CMD) -f conda-tools.mk conda-publish$(PYTHON_ENV)

check-recipe: ## Check recipe
	@$(MAKE_CMD) -f conda-tools.mk conda-recipe-check


# FAST TESTING
test-pytest:
	   @$(MAKE_CMD) -f test.mk
f-test: ## Test code with 'pytest' within a conda environment, this is the fastest way to test the code
ifneq ($(strip $(env)),)
	$(eval env=test)
endif
		 @$(MAKE) check-environment-test env=$(env)
	   @$(MAKE_CMD) -f conda-env.mk conda-run-env env=$(env) \
																					      cmd="make test-pytest"


# ENVIRONMENT CHECKING
ifeq (,$(shell which conda))
    HAS_CONDA=False
else
    HAS_CONDA=True
    ENV_DIR=$(shell conda info --base)
    MY_ENV_DIR=$(ENV_DIR)/envs/$(env)
    CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
endif
check-environment-%:
ifeq (True,$(HAS_CONDA))
ifneq ("$(wildcard $(MY_ENV_DIR))","") # check if the directory is there
		@echo ">>> Found '$(env)' environment in $(MY_ENV_DIR). Skipping installation..."
else
		@echo ">>> Detected conda, but $(env) is missing in $(ENV_DIR). Installing ..."
		@$(MAKE_CMD) -f conda-env.mk conda-create-env-$* env=$(env)
endif
else
    @echo ">>> Install conda first."
    @exit
endif
