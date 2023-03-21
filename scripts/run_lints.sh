#!/bin/bash
set -ex

black --check --diff .
mypy --install-types .
mypy --pretty --exclude tests .
