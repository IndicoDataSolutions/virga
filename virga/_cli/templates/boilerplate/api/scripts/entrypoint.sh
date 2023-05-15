#!/bin/bash

./scripts/prestart.sh

$@ >> $APP_LOG 2>&1 &
tail -Fq $APP_LOG
