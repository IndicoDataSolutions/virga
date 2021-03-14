#!/bin/bash

# enables host access of the web app via the container hostname.
# https://mageddo.github.io/dns-proxy-server/latest/en/
if ! docker ps | grep -q dns-proxy; then
    docker run --detach --rm --name dns-proxy -p 5380:5380 \
        -v /opt/dns-proxy-server/conf:/app/conf \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /etc/resolv.conf:/etc/resolv.conf \
        defreitas/dns-proxy-server > /dev/null
fi

docker run --rm -it --hostname app.indico.local $(docker build -q .)