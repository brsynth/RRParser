include ../../extras/.env
include ../.env

tmpfile = $(shell mktemp -u)
tmpdir  = $(shell dirname $(tmpfile))
test_env_file = $(tmpdir)/test_env_file.yml

PLATFORM = $(shell conda info | grep platform | awk '{print $$3}')

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## Basic help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help-advanced: ## Advanced help.
	@awk 'BEGIN {FS = ":.*?# "} /^[a-zA-Z_-]+:.*?# / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

CONDA_BUILD_ARGS = --quiet --numpy 1.11

MAKE_CMD = $(MAKE) -s --no-print-directory

clean: conda-clean-build

#python_versions = $(shell cat ../recipe/conda_build_config.yaml | awk 'NR>1 {print $$2}')
recipe_channels = $(shell cat ../../recipe/conda_channels.txt)
conda_channels  = $(shell conda config --show channels | awk '{print $2}')


# CONDA

## CONDA BASICS
### update
conda-update:
	@echo -n "Updating conda... "
	@conda update -q -y -n base -c defaults conda > /dev/null
	@echo OK
### install package
conda-install-%:
	@echo -n ">>> Installing $*... "
ifeq (,$(channel))
	@conda install -y $* > /dev/null
else
	@conda install -y -c $(channel) $* > /dev/null
endif
	@echo OK
### check recipe
conda-recipe-check:
	@echo -n "Checking the recipe... "
	@conda build --check $(CONDA_BUILD_ARGS) ../../recipe > /dev/null
	@echo OK
### clean build products
conda-clean-build:
	@rm -rf ${CONDA_BLD_PATH}/*
### Add channels specified in recipe
conda-add-channel-%:
	@conda config --quiet --add channels $* > /dev/null
## Check channels
conda-add-channels:
	@for channel in $(recipe_channels) ; do \
		$(MAKE_CMD) -f conda.mk conda-add-channel-$$channel ; \
	done

# Variants
ifneq ($(strip $(variants)),)
	VARIANTS = --variants=\"$(variants)\"
endif

## CONDA BUILD
### build only
conda-build-only: check-environment-build
	@echo -n "Building conda package... "
	@conda run --name ${PACKAGE}_build conda build --no-test $(CONDA_BUILD_ARGS) $(VARIANTS) --output-folder ${CONDA_BLD_PATH} ../../recipe > /dev/null
	@echo OK


# @for python_version in $(python_versions) ; do \
# 	$(MAKE_CMD) -f conda.mk conda-build-only_python$$python_version ; \
# done

### test only
# conda-test-only_python%: check-conda-build conda-add-channels
# 	@echo -n "Testing conda package for python$*... "
# 	@conda build --test $(CONDA_BUILD_ARGS) ${CONDA_BLD_PATH}/${PLATFORM}/${PACKAGE}-*py`echo $* | sed -e "s/\.//g"`*.tar.bz2
# 	@echo OK
# conda-test-only: check-conda-build conda-add-channels check-pyyaml
# 	@for python_version in $(python_versions) ; do \
# 		$(MAKE_CMD) -f conda.mk conda-test-only_python$$python_version ;\
# 	done
conda-test-only: check-environment-build conda-add-channels
	@echo -n "Testing conda package... "
	@conda run --name ${PACKAGE}_build conda build --test $(CONDA_BUILD_ARGS) ${CONDA_BLD_PATH}/${PLATFORM}/${PACKAGE}*.tar.bz2
	@echo OK

### build+test
conda-build: conda-build-test
# conda-build-test_python%: check-conda-build
# 	@echo -n "Building and Testing conda package... "
# 	@conda build $(CONDA_BUILD_ARGS) --python=$* --output-folder ${CONDA_BLD_PATH} ../../recipe > /dev/null
# 	@echo OK
# conda-build-test: check-conda-build check-pyyaml
# 	@for python_version in $(python_versions) ; do \
# 		$(MAKE_CMD) -f conda.mk conda-build-test_python$$python_version ;\
# 	done
conda-build: check-environment-build conda-add-channels
	@echo -n "Building and Testing conda package... "
	@conda run --name ${PACKAGE}_build conda build $(CONDA_BUILD_ARGS) $(VARIANTS) --output-folder ${CONDA_BLD_PATH} ../../recipe > /dev/null
	@echo OK

### convert
# conda-convert_python%: check-conda
# 	@echo -n "Converting conda package (python$*) from ${PLATFORM} to osx-64, linux-64 and win-64... "
# 	@conda convert \
# 	        --platform osx-64 \
# 	        --platform linux-64 \
# 	        --platform win-64 \
# 	        --output-dir ${CONDA_BLD_PATH} \
# 	        ${CONDA_BLD_PATH}/${PLATFORM}/${PACKAGE}-*py`echo $* | sed -e "s/\.//g"`*.tar.bz2 > /dev/null
# 	@echo OK
# conda-convert: check-conda
# 	@for python_version in $(python_versions) ; do \
# 		$(MAKE_CMD) -f conda.mk conda-convert_python$$python_version ;\
# 	done
conda-convert: check-conda
	@echo -n "Converting conda package from ${PLATFORM} to osx-64, linux-64 and win-64... "
	@conda run --name ${PACKAGE}_build \
		conda convert \
		        --platform osx-64 \
		        --platform linux-64 \
		        --platform win-64 \
		        --output-dir ${CONDA_BLD_PATH} \
		        ${CONDA_BLD_PATH}/${PLATFORM}/${PACKAGE}-*.tar.bz2 > /dev/null
	@echo OK


### publish
SECRETS = ../.secrets
ifneq ("","$(wildcard $(SECRETS))")
	ANACONDA_TOKEN = $(shell cat $(SECRETS) | grep ANACONDA_TOKEN | awk 'BEGIN {FS = "="} ; {print $$2}')
	ANACONDA_USER  = $(shell cat $(SECRETS) | grep ANACONDA_USER | awk 'BEGIN {FS = "="} ; {print $$2}')
endif
# conda-publish_python%: check-anaconda-client
# 	echo anaconda \
# 		--token ${ANACONDA_TOKEN} \
# 		upload \
# 		--user ${ANACONDA_USER} \
# 		--label ${ANACONDA_LABEL} \
# 		--skip-existing \
# 		${CONDA_BLD_PATH}/*/${PACKAGE}-*py`echo $* | sed -e "s/\.//g"`*.tar.bz2
# conda-publish: check-anaconda-client
# 	@for python_version in $(python_versions) ; do \
# 		$(MAKE_CMD) -f conda.mk conda-publish_python$$python_version ;\
# 	done
conda-publish:
	@echo -n "Publishing conda package... "
	conda run --name ${PACKAGE}_build \
		anaconda \
			--token ${ANACONDA_TOKEN} \
			upload \
			--user ${ANACONDA_USER} \
			--label ${ANACONDA_LABEL} \
			--skip-existing \
			${CONDA_BLD_PATH}/*/${PACKAGE}-*.tar.bz2


# ENVIRONMENT CHECKING
## Check conda
ifeq (,$(shell which conda))
    HAS_CONDA=False
else
    HAS_CONDA=True
    ENV_DIR=$(shell conda info --base)
    MY_ENV_DIR=$(ENV_DIR)/envs/$(env)
    CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
endif
check-conda:
ifeq (False,$(HAS_CONDA))
	$(error >>> Install conda first.)
endif

## Check conda-build
ifeq (,$(shell which conda-build))
    HAS_CONDA_BUILD=False
else
    HAS_CONDA_BUILD=True
endif
check-conda-build:
ifeq (False,$(HAS_CONDA_BUILD))
	echo conda env -n $(PACKAGE)_build create -f ../../recipe/conda_build_env.yaml
endif

# @$(MAKE_CMD) -f conda.mk conda-install-conda-build conda-install-conda-verify
# $(error >>> Install conda-build first.)

## Check anaconda-client
ifeq (,$(shell which anaconda))
    HAS_ANACONDA_CLIENT=False
else
    HAS_ANACONDA_CLIENT=True
endif
check-anaconda-client:
ifeq (False,$(HAS_ANACONDA_CLIENT))
	@$(MAKE_CMD) -f conda.mk conda-install-anaconda-client channel=conda-forge
endif

ifeq (,$(shell conda list | grep pyyaml))
    HAS_PYYAML=False
else
    HAS_PYYAML=True
endif
## Check pyyaml
check-pyyaml:
ifeq (False,$(HAS_PYYAML))
	@$(MAKE_CMD) -f conda.mk conda-install-pyyaml channel=conda-forge
endif

build_env_file = ../../recipe/conda_build_env.yaml
check_env_file = ../test/check-environment.yml
$(test_env_file): check-pyyaml
	@python3 ../$(TEST_PATH)/parse_recipe.py req > $(test_env_file)
check-environment-%: check-conda $(test_env_file)
ifneq ("$(wildcard $(MY_ENV_DIR))","") # check if the directory is there
		@echo ">>> Found '$(env)' environment in $(MY_ENV_DIR). Skipping installation..."
else
		@echo ">>> '$(env)' folder is missing in $(ENV_DIR)."
		@echo -n "Creating '$(env)' environment... "
		@conda env create -n $(env) -f $($(*)_env_file) > /dev/null
		@echo OK
endif

conda-run-env:
ifneq ($(strip $(cmd)),)
	@conda run --name $(env) $(cmd) $(args)
else
	@conda run --name $(env) \
		$(MAKE_CMD) -f conda.mk $(target) args=$(args)
endif
