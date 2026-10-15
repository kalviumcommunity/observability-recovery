#!/bin/sh
set -eu
python3 checks/local-context.py
echo "Deletes only namespace observability-recovery; its exercise PVC data will be lost."
kubectl delete namespace observability-recovery --ignore-not-found --wait=true
