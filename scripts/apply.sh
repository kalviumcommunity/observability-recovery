#!/bin/sh
set -eu
python3 checks/local-context.py
kubectl apply -f k8s/namespace.json
kubectl apply -f k8s/
echo "Inspect failures with kubectl -n observability-recovery get pods, describe pod, logs, get events."
