#!/bin/sh
set -eu
python3 checks/local-context.py
NS=observability-recovery
kubectl -n "$NS" delete pod traffic-probe --ignore-not-found --wait=true
kubectl -n "$NS" run traffic-probe --restart=Never --image=observability-recovery:1.0.0 --image-pull-policy=Never --command -- python3 -u -c '
import time,urllib.request
end=time.monotonic()+90
while time.monotonic()<end:
 try:
  with urllib.request.urlopen("http://cloudnotes:8080/health",timeout=1) as r:print(time.time(),r.status,flush=True)
 except Exception as e:print(time.time(),type(e).__name__,flush=True)
 time.sleep(.5)
'
