CloudNotes runs on local Kubernetes, but readiness is wrong, replacement Pods are misconfigured, monitoring is blind and alert evidence is unreliable. Repair operation and observability, then conduct one controlled Pod-recovery drill. The supplied image build and cluster bootstrap work and are not assessed.

You are the cloud engineer. Repair the supplied repository, validate the results locally and document the evidence in one PDF. All five tasks are compulsory. No cloud account, billing, paid registry, hosted CI or real secret is needed.

## Broken repository: fork and clone first

**Repository:** `https://github.com/kalviumcommunity/observability-recovery`

1. Open the repository and click **Fork**, or use the instructor-provided offline starter.
2. Clone your fork and create a branch:

```bash
git clone https://github.com/<your-username>/observability-recovery.git
cd observability-recovery
git checkout -b fix/assessment
```

3. Read `README.md` for the tested local setup, commands and checks.
4. Capture the initial failures before editing. Do not delete or bypass checks.

## Task 1 - Repair readiness behavior

Inspect Pod events and application routes. Fix the readiness probe path, preserving the working liveness probe and resource settings. Show the initial failed probe and final Ready state. Demonstrate that an intentionally unready Pod is excluded from Service endpoints; restore it afterwards.

**Evidence:** Original failure, relevant corrected file/diff, actual verification output and a short explanation.

## Task 2 - Repair replacement-Pod configuration

Inspect the Deployment desired state and provided runbook. Correct replicas to two for the stateless drill workload. Confirm two Ready Pods and a reachable Service. Delete one application Pod and record how the Deployment creates a replacement. Do not claim that scaling this stateless drill repairs a database or regional outage.

**Evidence:** Original failure, relevant corrected file/diff, actual verification output and a short explanation.

## Task 3 - Repair metrics collection

Inspect the supplied local Prometheus target and /metrics output. Fix its scrape target to the documented per-Pod metrics endpoints discovered through the headless cloudnotes-metrics Service. Run the supplied Prometheus and promtool containers inside the same local cluster/namespace; access their UI through loopback-only port-forward. Confirm target UP and query request count/error count/latency metrics before and after supplied traffic generator. Include dashboard or query screenshots and distinguish metrics from logs.

**Evidence:** Original failure, relevant corrected file/diff, actual verification output and a short explanation.

## Task 4 - Repair the user-impact alert

Fix the supplied Prometheus alert expression so it detects elevated failed-request ratio instead of successful-request ratio. Keep its given threshold, minimum-traffic guard and duration. Run promtool check rules and promtool test rules against supplied pass/fail fixtures. Generate controlled errors and show the alert firing and later clearing.

**Evidence:** Original failure, relevant corrected file/diff, actual verification output and a short explanation.

## Task 5 - Repair incident reporting and validate recovery

Fix reports/drill-template.json so elapsed recovery time is recorded in seconds rather than mislabeled milliseconds. Conduct the documented Pod-deletion drill, collect timestamped HTTP samples and Prometheus/log evidence, and report observed recovery against the supplied local target. Submit a short blameless incident timeline and one action item.  Do not infer database RPO or GCP-region RTO.

**Evidence:** Original failure, relevant corrected file/diff, actual verification output and a short explanation.

## Submission guidelines

Upload one PDF containing:

- name, section, environment/tool versions and forked repository URL or offline starter identifier;
- one labelled architecture or request-path diagram;
- Task 1 to Task 5 evidence, readable code/configuration excerpts and actual command output;
- original issue -> diagnosis -> fix -> verification summary;
- remaining limitations and the rebuild/cleanup procedure.

Use fake values only. Do not include real credentials, tokens, private keys, raw Terraform state or local secret files. A screenshot is not sufficient without the diagnosis and explanation. Equivalent valid commands are accepted. If a tool is unavailable, show the actual error and corrected files; static reasoning can earn applicable partial credit, but must not be presented as a passed runtime test.

## Simple evaluation rubric - 40 marks

| Marks | Criterion | Award marks for |
|---:|---|---|
| 8 | Readiness | Correct readiness path, Ready-state evidence and endpoint eligibility test. |
| 8 | Workload recovery | Two Ready stateless replicas and observed replacement after controlled Pod deletion. |
| 8 | Metrics collection | Reachable in-cluster scrape target, UP state and real changing request/error metrics. |
| 8 | Error alert | Correct failed-request ratio; rule tests pass; actual firing and clearing evidence. |
| 8 | Recovery analysis | Consistent time units, measured recovery, incident timeline and valid scope limitations. |

Award partial credit for correct diagnosis, repair and verification even when another task remains incomplete. Assess technical correctness and evidence of working behavior, not grammar, screenshot aesthetics or one prescribed wording. Task 5 has equal module shares; accept equivalent technically valid solutions.
