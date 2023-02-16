#!/bin/bash

# manually wait for noct since healthchecks don't seem
# to work (as of 3/18/21)
until (curl -sf http://noct:5000/api/ping); do
    ((count++))

    if [ ${count} -gt 500 ]; then
        echo "Noct unavailable"
        exit 1
    fi

    echo "Waiting for noct"
    sleep 0.5
done

pytest -vv tests
