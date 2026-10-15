#!/bin/sh
set -eu
python3 --version
git --version
docker version
docker compose version
echo "For Kubernetes: kubectl cluster-info, a pre-provisioned local cluster and local image access are required."
