#!/bin/bash
set -ex

black --check --diff .
mypy --pretty --exclude tests .
