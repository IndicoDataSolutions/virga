#!/bin/bash
set -e

poetry install -E linting

black --check --diff .
mypy --pretty --exclude tests .
