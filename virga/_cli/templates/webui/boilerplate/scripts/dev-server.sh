#!/bin/bash
set -e

# create a self-signed cert for https if none exists
if [ ! -f snowpack.key ]; then
    npx mkcert create-ca
    npx mkcert create-cert --key snowpack.key --cert snowpack.crt --domains app.indico.local
fi

yarn start