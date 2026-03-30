# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 2
- Succeeded: 0
- Stalled: 0
- Failed: 0
- Pending: 2

## Campaign Health

- active=2 pending=2 running=1 completed=0 failed=0
- structured ingestion success rate: 0.0
- semantic reuse rate: 0.0
- transfer usage rate: 0.0
- reusable structure rate: 0.0
- obstruction discovery rate: 0.0
- high-priority frontier share: 0.571
- repeated no-signal streak: 0
- duplicate frontier pressure: 0
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
- `QUEUED`: 1

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
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_submit_stderr.txt` (54 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_submit_stdout.txt` (0 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

## Incidents

- No open incidents.

## Audit Trail

- No audit events.

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 14
- jobs synced: 1
- jobs submitted: 1
- active before: 1
- active after: 2
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=0, subgoals=0, traces=0
- synced `bff4c05f-d103-47ac-83f8-1164972a1bca` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- queued `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` for `erdos-123` via `promote_lemma` / `invariant_mining` (chosen by deterministic fallback policy; move_family=invariant_mining; rationale=Recurring semantic signal 'unknown' suggests a hidden invariant worth isolating.)
- selected `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` rank=1 score=9.6525
- considered `fcb72bba-56ee-4d02-94da-0d731f81f87c` rank=2 score=9.491
- considered `8c94cac0-f921-46b2-9ea8-b528bf049489` rank=3 score=2.41
- considered `6f5f6049-a081-431f-94b4-a6967febd8e3` rank=4 score=2.41
- considered `2b1ae22c-2fa4-469a-83fc-2a5638655b03` rank=5 score=2.41
- skipped `2b1ae22c-2fa4-469a-83fc-2a5638655b03` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `be68c489-52d5-48b9-a696-68de3f593ff2` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `316860b7-2acd-425f-b7fe-716bad8de4f3` for `erdos-123` (frontier throttled for duplicate move-family pressure)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
