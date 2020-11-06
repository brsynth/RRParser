include ../.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help


help: ## Basic help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

MAKE_CMD = $(MAKE) -s

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

# PYTHON VERSION
ifneq ($(strip $(python)),)
	PYTHON = python=$(python)
endif


conda-create-env-check: ## conda-create-env: Create conda environment named by 'env=<name>' cli argument. If 'python=<version>' cli argument is passed, python=<version> will be installed within the environment.
	@echo -n "Creating 'check' environment... "
	@conda create -y -n $(env) $(PYTHON) > /dev/null
	@conda env update -n $(env) --file ../$(CHECK_PATH)/check-environment.yml > /dev/null
	@echo OK

conda-create-env-test: ## conda-create-env: Create conda environment named by 'env=<name>' cli argument. If 'python=<version>' cli argument is passed, python=<version> will be installed within the environment.
	@echo -n "Creating 'test' environment... "
	@$(MAKE_CMD) -f conda-env.mk conda-create-env-check env=$(env)
	@$(MAKE_CMD) -f conda-tools.mk conda-install-pyyaml
	@python ../$(TEST_PATH)/parse_recipe.py > /dev/null
	@conda env update -n $(env) --file ../$(TEST_PATH)/test-environment.yml > /dev/null
	@rm -f ../$(TEST_PATH)/environment.yml
	@echo OK

conda-run-env:
ifneq ($(strip $(cmd)),)
	@conda run --name $(env) $(cmd)
else
	@conda run --name $(env) \
		$(MAKE_CMD) -f conda-tools.mk $(target)
endif


# conda-create-env-build:
# 	@echo -n "Creating 'build' environment... " && \
# 	conda env create -q -n $(env) --file ../recipe/conda_build_env.yaml > /dev/null || true && \
# 	echo OK
#
#
#
# # Process operations within conda environment
# conda-%:
# 	@conda run --name $(env) \
# 		$(MAKE) -f conda-tools.mk conda-$*
#
# # Process other operations within conda environment passed in cli arg
# %:
# 	@conda run --name $(env) \
# 		$(MAKE) -f conda-tools.mk $@ $(ARGS)
