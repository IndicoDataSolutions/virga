#!/bin/bash

# wait for postgres
# while ! pg_isready -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER}" -p 5432; do
#     sleep 1;
# done

# run pending migrations
# alembic upgrade head
