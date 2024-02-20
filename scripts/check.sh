#! /bin/bash

set -e

black src/pte/ --check --quiet && echo "Passed: black" || { echo "Failed: black"; exit 1; }
isort src/pte/ --check --quiet && echo "Passed: isort" || { echo "Failed: isort"; exit 1; }
mypy --package pte --no-error-summary && echo "Passed: mypy" || { echo "Failed: mypy"; exit 1; }

echo "All checks passed."
