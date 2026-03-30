# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 1
- Succeeded: 0
- Stalled: 0
- Failed: 0
- Pending: 1

## Campaign Health

- active=1 pending=1 running=0 completed=0 failed=0
- structured ingestion success rate: 0.0
- semantic reuse rate: 0.0
- transfer usage rate: 0.0
- reusable structure rate: 0.0
- obstruction discovery rate: 0.0
- high-priority frontier share: 0.533
- repeated no-signal streak: 0
- duplicate frontier pressure: 0
- move-family diversity: frontier=10 completed=0
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
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `72d3ca62-8ac6-4088-9d37-1d9f45d71fa4`
- external status: `QUEUED`
- objective: Fill in all sorries. Strip imports to expose hidden dependencies. Report intermediate lemmas or unresolved goals. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Minimal context is the safest first pass for exposing missing structure.
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_submit_stderr.txt` (54 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_submit_stdout.txt` (0 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

## Incidents

- No open incidents.

## Audit Trail

- No audit events.

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 15
- jobs synced: 0
- jobs submitted: 1
- active before: 0
- active after: 1
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=0, subgoals=0, traces=0
- queued `bff4c05f-d103-47ac-83f8-1164972a1bca` for `erdos-123` via `underspecify` / `legacy.underspecify` (chosen by deterministic fallback policy; move_family=legacy.underspecify; rationale=Minimal context is the safest first pass for exposing missing structure.)
- selected `bff4c05f-d103-47ac-83f8-1164972a1bca` rank=1 score=6.79
- considered `64f09d80-dd48-4a75-aaff-1439367f38da` rank=2 score=6.81
- considered `8dee98ae-3ce1-48fc-ad80-6542462ad3e3` rank=3 score=6.81
- considered `d60ecec3-bd00-43c3-9e95-a74e54e037a9` rank=4 score=6.81
- considered `ce470af6-b94b-47f7-8474-fd0eb880aea0` rank=5 score=6.31
- skipped `d60ecec3-bd00-43c3-9e95-a74e54e037a9` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `ce470af6-b94b-47f7-8474-fd0eb880aea0` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `bf67ff6b-246b-442c-a9d2-96e69076a9a5` for `erdos-123` (frontier throttled for duplicate move-family pressure)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
