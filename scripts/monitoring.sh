#!/bin/sh
set -eu
python3 checks/local-context.py
NS=observability-recovery
kubectl -n "$NS" create configmap prometheus-config --from-file=monitoring/prometheus.yml --from-file=monitoring/alerts.yml --from-file=monitoring/rules.test.yml --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f monitoring/deployment.json
kubectl -n "$NS" rollout restart deployment/prometheus
kubectl -n "$NS" rollout status deployment/prometheus --timeout=120s
