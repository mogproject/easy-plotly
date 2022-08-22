#!/bin/bash

SCRIPT_DIR=$( cd "$( dirname "$0" )" && pwd -P )
PROJECT_DIR=$( dirname "${SCRIPT_DIR}" )

for f in ${PROJECT_DIR}/notebooks/*.ipynb; do
  echo "Clearing output: ${f}"
  jupyter nbconvert --clear-output --inplace "${f}"
done
