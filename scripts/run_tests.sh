#!/bin/bash

until (curl -sf "http://${POSTGRES_HOST}:5000/api/ping"); do
    ((count++))

    if [ ${count} -gt 500 ]; then
        echo "Noct unavailable"
        exit 1
    fi

    echo "Waiting for noct"
    sleep 0.5
done

pytest -vv tests
