# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 3
- Succeeded: 0
- Stalled: 0
- Failed: 0
- Pending: 3

## Campaign Health

- active=3 pending=3 running=1 completed=0 failed=0
- structured ingestion success rate: 0.0
- semantic reuse rate: 0.0
- transfer usage rate: 0.0
- reusable structure rate: 0.0
- obstruction discovery rate: 0.0
- high-priority frontier share: 0.571
- repeated no-signal streak: 0
- duplicate frontier pressure: 2
- move-family diversity: frontier=9 completed=0
- open incidents: 0

## Version Drift

- No manifest version drift detected.

## Discovery Graph

- nodes: 0
- edges: 0
- verified-like nodes: 0
- No discovery nodes yet.

## Discovery Questions

- No open discovery questions.

## Conjecture Tuning

### Erdos Problem 123: d-complete triple-power antichain sums

- seed question [boundary_case]: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- seed question [bridge_lemma]: Which reusable covering or divisibility-extraction lemmas recur across special parameter triples and look strong enough to promote?
- seed question [transfer]: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- focus areas: d-completeness boundary cases, special parameter triples, reusable covering lemmas, antichain and divisibility extraction lemmas, obstruction patterns and counterexamples, bridge lemmas from solved motifs, transfer-worthy motifs
- preferred move families: invariant_mining, extremal_case, decompose_subclaim, equivalent_view, witness_minimization, adversarial_counterexample, transfer_reformulation

## Active jobs

- `IN_PROGRESS`: 1
- `QUEUED`: 2

## Recently completed

- None yet.

## Recurring lemmas

- None yet.

## Space Search Progress

- recurring lemmas: none stabilized yet
- recurring subgoals: none stabilized yet
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- no recurring lemmas have stabilized yet
- no repeated subgoals captured yet
- no blocker patterns aggregated yet

## Assumption sensitivity

- None yet.

## Experiment log

### bff4c05f-d103-47ac-83f8-1164972a1bca

- move: `underspecify`
- move family: `legacy.underspecify`
- theorem family: `erdos_problem`
- phase: `mapping`
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `72d3ca62-8ac6-4088-9d37-1d9f45d71fa4`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. Strip imports to expose hidden dependencies. Report intermediate lemmas or unresolved goals. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Minimal context is the safest first pass for exposing missing structure.
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt` (8771 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stderr.txt`
- notes: Aristotle job 72d3ca62-8ac6-4088-9d37-1d9f45d71fa4 is still in progress.

### b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21

- move: `promote_lemma`
- move family: `invariant_mining`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `67636ee5-eb7b-461b-9fcd-0f9d100ddba0`
- external status: `QUEUED`
- objective: Fill in all sorries. Mine a reusable invariant or monotonicity principle that explains the recurring signal 'unknown'. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring semantic signal 'unknown' suggests a hidden invariant worth isolating.
- campaign priority: 1.75
- transfer score: 0.3125
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt` (8771 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt`
- notes: Aristotle job 67636ee5-eb7b-461b-9fcd-0f9d100ddba0 is still queued.

### 9941d619-a8ab-4ac9-ab9c-1503088b4e65

- move: `promote_lemma`
- move family: `decompose_subclaim`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `51be99fa-6b9b-4c6c-9df5-898433246f61`
- external status: `QUEUED`
- objective: Fill in all sorries. Split the current theorem into a bridge lemma and a remaining reduction built around the recurring subgoal. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Campaign seed 'derive a covering lemma that upgrades interval coverage to eventual d-completeness' is an explicitly requested bridge lemma target.
- campaign priority: 1.7
- transfer score: 0.3
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt` (8771 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt`
- notes: Aristotle job 51be99fa-6b9b-4c6c-9df5-898433246f61 is still queued.

## Incidents

- No open incidents.

## Audit Trail

- No audit events.

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 14
- jobs synced: 3
- jobs submitted: 0
- active before: 3
- active after: 3
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=0, subgoals=0, traces=0
- synced `bff4c05f-d103-47ac-83f8-1164972a1bca` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `9941d619-a8ab-4ac9-ab9c-1503088b4e65` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- considered `4d7f01cc-8515-4adc-8502-b99e917e6bdf` rank=1 score=-4.1475
- considered `be92880d-4ee5-4bd1-a69f-ebc53f41eabb` rank=2 score=-4.309
- selected `f4853891-1ebb-4f1a-94e1-2448bbf4a663` rank=3 score=-6.39
- considered `f36b61f7-6183-489d-b981-421c17daa091` rank=4 score=-6.39
- considered `f0335529-6f25-4011-9174-80296b3de70c` rank=5 score=-6.39
- skipped `f0335529-6f25-4011-9174-80296b3de70c` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `8ede7f19-0b7f-41cd-8d07-3ac095da7afd` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `4f5ada89-3505-49fc-9e2b-6cbc0f57dcb2` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `4d7f01cc-8515-4adc-8502-b99e917e6bdf` for `erdos-123` (duplicate active experiment signature)
- skipped `be92880d-4ee5-4bd1-a69f-ebc53f41eabb` for `erdos-123` (duplicate active experiment signature)

## Suggested next move

- Continue assumption perturbation and equivalent reformulations to sharpen the boundary map.
