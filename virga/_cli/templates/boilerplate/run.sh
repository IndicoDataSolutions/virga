#!/bin/bash

# enables host access of the nginx app via the container hostname
# https://github.com/dvddarias/docker-hoster
if ! docker ps | grep -q dns-proxy; then
    echo "Spawning DNS proxy server for container hostname resolution..."
    docker run --rm -d --name dns-proxy \
        -v /var/run/docker.sock:/tmp/docker.sock \
        -v /etc/hosts:/tmp/hosts \
        dvdarias/docker-hoster
fi

docker-compose up