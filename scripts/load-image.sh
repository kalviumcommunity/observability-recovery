#!/bin/sh
set -eu
IMAGE=observability-recovery:1.0.0
docker image inspect "$IMAGE" >/dev/null
CONTEXT=$(kubectl config current-context)
case "$CONTEXT" in
  kind-*) kind load docker-image "$IMAGE" --name "${CONTEXT#kind-}" ;;
  minikube) minikube image load "$IMAGE" ;;
  docker-desktop) echo "Docker Desktop may have a separate Kubernetes image store. Instructor must preload and verify images; canonical tested route is kind." >&2; exit 1 ;;
  *) echo "Unsupported context $CONTEXT. Instructor must configure a local image-loading route. No remote cluster allowed." >&2; exit 1 ;;
esac
