#!/bin/bash

source .env

#bash ./scripts/clean_env.sh

conda build --no-test \
     -c brsynth \
     -c conda-forge \
     --output-folder ${CONDA_BLD_PATH} ../recipe
