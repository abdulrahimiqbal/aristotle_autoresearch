# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 4
- Succeeded: 0
- Stalled: 1
- Failed: 0
- Pending: 3

## Campaign Health

- active=3 pending=3 running=3 completed=1 failed=0
- structured ingestion success rate: 1.0
- semantic reuse rate: 0.0
- transfer usage rate: 1.0
- reusable structure rate: 1.0
- obstruction discovery rate: 1.0
- high-priority frontier share: 0.5
- repeated no-signal streak: 0
- duplicate frontier pressure: 2
- move-family diversity: frontier=9 completed=1
- open incidents: 2

## Version Drift

- No manifest version drift detected.

## Discovery Graph

- nodes: 3
- edges: 2
- verified-like nodes: 0
- `experiment` `9941d619-a8ab-4ac9-ab9c-1503088b4e65` confidence=1.0 provenance=execution
- `reproducible_candidate_lemma` `bridge_interval_coverage : True` confidence=0.75 provenance=artifact
- `reproducible_candidate_lemma` `promoted_lemma : True` confidence=0.75 provenance=artifact

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

- `IN_PROGRESS`: 3

## Recently completed

- `9941d619-a8ab-4ac9-ab9c-1503088b4e65` on `erdos-123` -> `stalled`

## Recurring lemmas

- `bridge_interval_coverage : True` — reuse=2
- `promoted_lemma : True` — reuse=2

## Space Search Progress

- recurring lemmas: 2 clusters
- recurring subgoals: none stabilized yet
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- recurring lemmas are beginning to cluster across runs
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
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt` (8756 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stderr.txt`
- notes: Aristotle job 72d3ca62-8ac6-4088-9d37-1d9f45d71fa4 is still in progress.

### b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21

- move: `promote_lemma`
- move family: `invariant_mining`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `67636ee5-eb7b-461b-9fcd-0f9d100ddba0`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. Mine a reusable invariant or monotonicity principle that explains the recurring signal 'unknown'. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring semantic signal 'unknown' suggests a hidden invariant worth isolating.
- campaign priority: 1.75
- transfer score: 0.3125
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt` (8756 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt`
- notes: Aristotle job 67636ee5-eb7b-461b-9fcd-0f9d100ddba0 is still in progress.

### 9941d619-a8ab-4ac9-ab9c-1503088b4e65

- move: `promote_lemma`
- move family: `decompose_subclaim`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `51be99fa-6b9b-4c6c-9df5-898433246f61`
- external status: `COMPLETE`
- objective: Fill in all sorries. Split the current theorem into a bridge lemma and a remaining reduction built around the recurring subgoal. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Campaign seed 'derive a covering lemma that upgrades interval coverage to eventual d-completeness' is an explicitly requested bridge lemma target.
- campaign priority: 1.7
- transfer score: 0.3
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; generated=2
- new signal count: 2
- reused signal count: 0
- generated lemmas:
  - `bridge_interval_coverage : True`
  - `promoted_lemma : True`
- candidate lemmas:
  - `bridge_interval_coverage : True`
  - `promoted_lemma : True`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt` (8776 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin` (2859 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/ARISTOTLE_SUMMARY_51be99fa-6b9b-4c6c-9df5-898433246f61.md` (1762 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/Main.lean` (2007 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lakefile.toml` (152 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lean-toolchain` (25 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stderr.txt` (247 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/ARISTOTLE_SUMMARY_51be99fa-6b9b-4c6c-9df5-898433246f61.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/README.md`
- evaluation total: 13.74
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### ddb1aae2-1b93-438c-9165-39a34b6f05c6

- move: `promote_lemma`
- move family: `legacy.promote_lemma`
- theorem family: `erdos_problem`
- phase: `stress_testing`
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `111c2eb8-0247-4974-8ea6-64a151b5af34`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring lemma 'bridge_interval_coverage : True' crossed the promotion threshold.
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt` (8756 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt`
- notes: Aristotle job 111c2eb8-0247-4974-8ea6-64a151b5af34 is still in progress.

## Incidents

- `warning` `retry_budget_exhausted`: Experiment b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21 reached retry budget (7 attempts).
- `warning` `retry_budget_exhausted`: Experiment bff4c05f-d103-47ac-83f8-1164972a1bca reached retry budget (8 attempts).

## Audit Trail

- `experiment_finalized` at `2026-03-30T23:56:33.332007+00:00`
- `result_ingested` at `2026-03-30T23:56:33.322940+00:00`

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 14
- jobs synced: 3
- jobs submitted: 0
- active before: 3
- active after: 3
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=2, subgoals=0, traces=0
- synced `bff4c05f-d103-47ac-83f8-1164972a1bca` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `ddb1aae2-1b93-438c-9165-39a34b6f05c6` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- considered `7ef8eb27-b4ed-4fa9-948a-597e3972f46d` rank=1 score=-5.3675
- considered `d0b8b453-544c-4328-9f2a-c80713b91d67` rank=2 score=-10.68
- selected `0538346a-8f8c-4565-b8b1-7ed47ff63d0e` rank=3 score=-7.79
- considered `c85dcfab-b6b4-4146-8335-8ba20f3090c9` rank=4 score=-7.79
- considered `45da5d2d-4c1e-47cc-8f44-24c2572d4eed` rank=5 score=-7.79
- skipped `45da5d2d-4c1e-47cc-8f44-24c2572d4eed` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `7a3b0382-f929-4c5d-8f2c-b14f3b917eba` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `218ac445-c783-41fd-901e-c22eb32e2802` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `7ef8eb27-b4ed-4fa9-948a-597e3972f46d` for `erdos-123` (duplicate active experiment signature)
- skipped `d0b8b453-544c-4328-9f2a-c80713b91d67` for `erdos-123` (duplicate active experiment signature)

## Suggested next move

- Promote the top recurring lemma into a standalone theorem if not already tested.
