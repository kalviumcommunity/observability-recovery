#!/bin/sh
set -eu
. ./network/request.env
curl --noproxy '*' --fail --show-error --silent --max-time 5 --resolve "$HOSTNAME:18083:127.0.0.1" "http://notes.test:18083/health"
