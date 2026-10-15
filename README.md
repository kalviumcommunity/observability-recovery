# observability-recovery

Local Cloud Computing assessment starter.


## Environment and zero-cost boundary

Use Python 3.10+, Git, curl and an instructor-preinstalled free OCI engine with Compose.
Canonical free route: Linux Docker Engine (or instructor-tested Podman compatibility).
macOS may use free Colima/Lima; Docker Desktop is optional only if free use is permitted
by its license. No paid account, cloud project, registry login, trial credits or hosted CI.
Application images use Python 3.12.12 and the standard library only. Base images are pinned
to verified multi-architecture digests. Initial public image downloads need internet; instructor
should preload/cache images for the exam to avoid rate limits. Local power, hardware and
internet are assumed, not supplied. Use a free text editor, diagrams.net/Excalidraw or plain
Markdown for diagrams; export PDF with a free browser/office suite. No paid PDF tool required.

Reference environment: macOS arm64, Docker Engine 29.4.3, kind 0.30.0 local Kubernetes
v1.34.0. Docker Desktop was the host engine, not a mandatory licensed dependency. This records the author's test environment, not a requirement to purchase Docker
Desktop. Other runtime/OS combinations need instructor validation. Linux/WSL2 recommended
for native CLI commands; use WSL paths for executable shell scripts. Run shell scripts from
repository root. chmod +x scripts/*.sh if an archive lost executable bits.

Practical host allowance: 4 CPU, 8 GB RAM, 8 GB free disk for container-only work; 4 CPU,
12 GB RAM, 12 GB free disk for Kubernetes work (allocate >=4 GB to the engine). These are
planning recommendations, not measured minimums. Instructor installs tools and warms caches
before the timed assessment. Allow a provisional 2-3 hour practical window, then calibrate
with a representative student; this is not a measured student completion time.

There are five planted assessment issues, one per task. Setup and tools are not extra faults.
Some symptoms interact. Use the task ordering below and static checks to diagnose tasks even
when earlier runtime work is incomplete. Do not delete checks, force success or change the
specified ports/contracts. Exercise cloud policy models are design validation only, not real
GCP enforcement. Keep your changes and evidence scoped to this repository.

Read [STUDENT_TASKS.md](STUDENT_TASKS.md) for the exact assessment and rubric.

## Evidence and safe cleanup

Start from reports/report-template.md and release-notes.md. Store local transcripts under
ignored evidence/. Never commit real secrets, generated plans/state or local .env. Fake demo
identity strings end in example.invalid. No real GCP operations are performed.
Run scripts/cleanup.sh when finished; it deletes only this exercise's services/namespace.
Do not run system-wide docker prune, reset Kubernetes or delete unrelated namespaces.

## Workflow and local cluster prerequisites

Instructor supplies a local Kubernetes cluster with kubectl and a working image loader.
The supplied image and bootstrap are healthy and unassessed. No cloud LoadBalancer or managed
monitoring. Two replicas serve a read-only fixture; no stateful database recovery is assessed.

```bash
docker build -t observability-recovery:1.0.0 .
./scripts/load-image.sh
./scripts/apply.sh
python3 checks/check.py probe
python3 checks/check.py replicas
kubectl -n observability-recovery get pods
kubectl -n observability-recovery describe deployment cloudnotes
```

Task 1: preserve /health liveness, fix the readiness contract, apply changes, inspect Pod Ready
conditions and EndpointSlice conditions. To demonstrate exclusion safely, choose ONE Pod and
create /tmp/not-ready using kubectl exec; wait for its Ready condition to turn false, inspect
EndpointSlice ready:false, remove the file and wait for recovery. EndpointSlices may retain an
unready entry with ready:false; it is not eligible for ordinary Service traffic. Do not expect
the entry always to disappear.
Task 2: set the required two replicas, then observe replacement of one deleted application Pod.
Task 3/4: local Prometheus Deployment is provided; config lives in monitoring/:

```bash
./scripts/monitoring.sh
python3 checks/check.py metrics
./scripts/rule-check.sh
kubectl -n observability-recovery port-forward service/cloudnotes 18083:8080 --address 127.0.0.1
# Separate terminal:
kubectl -n observability-recovery port-forward deployment/prometheus 19093:9090 --address 127.0.0.1
```

Open http://127.0.0.1:19093/targets, /query and /alerts. First repair readiness so app Service
endpoints are eligible. Prometheus discovers each Pod through the headless cloudnotes-metrics Service and scrapes
port 8080 inside the namespace, not host loopback. The planted port defect is 8081. Do not
scrape a load-balanced Service address for replica counters: alternating instances corrupt
rate calculations. DNS-discovered Pod targets retain separate instance labels. promtool comes in the same pinned free Prometheus image. ConfigMap changes require
scripts/monitoring.sh again. Capture rule-check and actual alert behavior, not one instead of the
other. Fixtures cover healthy and failing traffic, with the minimum-traffic guard preserved.

```bash
python3 scripts/traffic.py http://127.0.0.1:18083 /health 20
python3 scripts/traffic.py http://127.0.0.1:18083 /fail 75
# Capture alert firing after its documented 10s pending + rolling window.
python3 scripts/traffic.py http://127.0.0.1:18083 /health 75
# Capture cleared alert. This sample needs ~3 minutes; traffic stops automatically.
```

Task 5: reports/drill-template.json and scripts/sample-recovery.py. Before run, ensure desired
replicas are healthy and Prometheus is collecting. Sampler deletes ONE application Pod, records
HTTP observations and Ready count for up to 90 seconds, and writes ignored evidence/recovery.json.
Restart port-forward if it followed the deleted Pod; that tunnel loss is not proof of Service
outage. Record the limitation or use the documented in-cluster probe. The 60-second target is
local Pod-replica restoration only, not database RPO or GCP-region RTO. If no user request fails,
report zero observed failures honestly; do not invent downtime.

```bash
python3 scripts/sample-recovery.py
python3 checks/check.py report
kubectl -n observability-recovery logs -l app=cloudnotes --tail=20
```

For stable user-traffic evidence during Pod replacement use scripts/start-probe.sh, then
kubectl -n observability-recovery logs pod/traffic-probe. It sends bounded in-cluster HTTP
requests for 90 seconds and records actual status/time samples without port-forward coupling. Author validation covers one-Pod deletion, not node failure.
