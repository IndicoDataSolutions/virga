#!/bin/bash

until (curl -sf "${NOCT_HOST:-http://noct:5000}/api/ping"); do
    ((count++))

    if [ ${count} -gt 200 ]; then
        echo "Noct unavailable"
        exit 1
    fi

    echo "Waiting for noct"
    sleep 1
done

pytest -vv tests
