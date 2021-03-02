#!/bin/bash
set -e
echo "starting" > /var/log/foo
tail -Fq /var/log/foo
