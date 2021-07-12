#!/bin/bash

black --check --diff .
mypy --pretty .