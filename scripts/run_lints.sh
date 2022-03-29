#!/bin/bash

poetry install -E linting

black --check --diff .
mypy --pretty --exclude tests .