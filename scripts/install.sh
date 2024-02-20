#!/bin/bash

# Installs the application into the ~/.local tree.
# The application can be run using 'pte' if ~/.local/bin is in $PATH.
# Dependencies are installed into ~/.local/lib.

set -e

PROJECT_NAME=pte
EXECUTABLE_NAME=pte

LIB_PATH=${HOME}/.local/lib/${PROJECT_NAME}
EXECUTABLE_PATH=${HOME}/.local/bin/${EXECUTABLE_NAME}
VENV_PATH=${LIB_PATH}/venv

set -x
 
# Remove existing installation
rm -rf "${LIB_PATH}"
rm -f "${EXECUTABLE_PATH}"

# Create venv
mkdir "${LIB_PATH}"
python -m venv "${VENV_PATH}"

# Install application into venv
"${VENV_PATH}/bin/pip" install .

# Create executable
echo "\"${VENV_PATH}/bin/python\" -m pte.run \"\$@\"" > ${EXECUTABLE_PATH}
chmod +x ${EXECUTABLE_PATH}
