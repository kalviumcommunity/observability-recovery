#!/bin/sh
set -eu
NS=observability-recovery
kubectl -n "$NS" exec deployment/prometheus -- promtool check rules /etc/prometheus/alerts.yml
kubectl -n "$NS" exec deployment/prometheus -- promtool test rules /etc/prometheus/rules.test.yml
