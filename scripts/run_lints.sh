#!/bin/bash

black --check --diff .
yes 2>/dev/null | mypy --install-types
mypy --pretty .