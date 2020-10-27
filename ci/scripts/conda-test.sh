#!/bin/bash

source .env
source ../extras/.env

conda build --test \
        -c brsynth \
        -c conda-forge \
        ${CONDA_BLD_PATH}/*/${PACKAGE}-*.tar.bz2
