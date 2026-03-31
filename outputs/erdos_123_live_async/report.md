# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 4
- Succeeded: 0
- Stalled: 2
- Failed: 0
- Pending: 2

## Campaign Health

- active=2 pending=2 running=2 completed=2 failed=0
- structured ingestion success rate: 1.0
- semantic reuse rate: 0.333
- transfer usage rate: 0.5
- reusable structure rate: 1.0
- obstruction discovery rate: 0.5
- high-priority frontier share: 0.5
- repeated no-signal streak: 0
- duplicate frontier pressure: 1
- move-family diversity: frontier=9 completed=2
- open incidents: 2

## Version Drift

- `manifest_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `prompt_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `move_registry_version` historical=`2026.03.phase4` current=`2026.03.phase7` count=26
- `runtime_policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26

## Discovery Graph

- nodes: 4
- edges: 3
- verified-like nodes: 0
- `experiment` `9941d619-a8ab-4ac9-ab9c-1503088b4e65` confidence=1.0 provenance=execution
- `experiment` `ddb1aae2-1b93-438c-9165-39a34b6f05c6` confidence=1.0 provenance=execution
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

- `IN_PROGRESS`: 2

## Recently completed

- `ddb1aae2-1b93-438c-9165-39a34b6f05c6` on `erdos-123` -> `stalled`
- `9941d619-a8ab-4ac9-ab9c-1503088b4e65` on `erdos-123` -> `stalled`

## Recurring lemmas

- `promoted_lemma : True` — reuse=4
- `bridge_interval_coverage : True` — reuse=2

## Space Search Progress

- recurring lemmas: 2 clusters
- recurring subgoals: none stabilized yet
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- recurring lemmas are beginning to cluster across runs
- no repeated subgoals captured yet
- no blocker patterns aggregated yet
- move `promote_lemma` repeatedly yields blocker `unknown` / `partial` (2 runs)

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
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt` (8746 bytes)
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
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt` (8746 bytes)
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
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `111c2eb8-0247-4974-8ea6-64a151b5af34`
- external status: `COMPLETE`
- objective: Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring lemma 'bridge_interval_coverage : True' crossed the promotion threshold.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; generated=1
- new signal count: 0
- reused signal count: 1
- generated lemmas:
  - `promoted_lemma : True`
- candidate lemmas:
  - `promoted_lemma : True`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt` (8756 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin` (2532 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/ARISTOTLE_SUMMARY_111c2eb8-0247-4974-8ea6-64a151b5af34.md` (2170 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/AristotleWorkspace.lean` (332 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/Main.lean` (332 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lakefile.toml` (206 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lean-toolchain` (25 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/ARISTOTLE_SUMMARY_111c2eb8-0247-4974-8ea6-64a151b5af34.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/AristotleWorkspace.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/README.md`
- evaluation total: 4.75
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

## Incidents

- `warning` `retry_budget_exhausted`: Experiment b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21 reached retry budget (11 attempts).
- `warning` `retry_budget_exhausted`: Experiment bff4c05f-d103-47ac-83f8-1164972a1bca reached retry budget (12 attempts).

## Audit Trail

- `experiment_finalized` at `2026-03-31T00:34:30.555919+00:00`
- `result_ingested` at `2026-03-31T00:34:30.550974+00:00`
- `experiment_finalized` at `2026-03-30T23:56:33.332007+00:00`
- `result_ingested` at `2026-03-30T23:56:33.322940+00:00`

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 14
- jobs synced: 2
- jobs submitted: 0
- active before: 2
- active after: 2
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=2, subgoals=0, traces=0
- synced `bff4c05f-d103-47ac-83f8-1164972a1bca` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- considered `2e107a1c-152a-4ef3-a426-203cb82d8a8e` rank=1 score=179.4144
- considered `54f87738-e0d3-4103-8ddb-35c0e246aaaf` rank=2 score=179.4144
- considered `5a67ec35-8918-4308-bd84-ca9d549ab223` rank=3 score=179.4144
- considered `9e84ddeb-2479-4dc6-a862-4e20e2936487` rank=4 score=178.9144
- considered `9f7a745a-e14f-457e-8b8a-50757ccc69ef` rank=5 score=178.9144
- skipped `3b89a65f-1f86-4f35-a913-ccb051a981ac` for `erdos-123` (duplicate active experiment signature)
- skipped `b71e8368-6a5c-4c5f-b62c-28eb41720a3f` for `erdos-123` (conjecture active cap reached)
- skipped `554d1b56-9b57-48dc-b12e-f8901a553206` for `erdos-123` (conjecture active cap reached)
- skipped `fbf96373-7bf5-4810-aa0f-6f599be15935` for `erdos-123` (conjecture active cap reached)
- skipped `18ce567d-d37a-4d6c-ace2-40d5939e5c00` for `erdos-123` (conjecture active cap reached)
- skipped `42b2742f-00b7-4067-b9eb-e5efd5601653` for `erdos-123` (conjecture active cap reached)
- skipped `baf5a087-4650-410a-86d0-ab70fb7e00cd` for `erdos-123` (conjecture active cap reached)
- skipped `b81496cf-89f5-4486-97b9-9aafcc336a0d` for `erdos-123` (conjecture active cap reached)
- skipped `2e107a1c-152a-4ef3-a426-203cb82d8a8e` for `erdos-123` (conjecture active cap reached)
- skipped `54f87738-e0d3-4103-8ddb-35c0e246aaaf` for `erdos-123` (conjecture active cap reached)
- skipped `5a67ec35-8918-4308-bd84-ca9d549ab223` for `erdos-123` (conjecture active cap reached)
- skipped `9e84ddeb-2479-4dc6-a862-4e20e2936487` for `erdos-123` (conjecture active cap reached)
- skipped `9f7a745a-e14f-457e-8b8a-50757ccc69ef` for `erdos-123` (conjecture active cap reached)
- skipped `2236fdb8-1896-487e-92ad-d3ac9c0714ad` for `erdos-123` (conjecture active cap reached)

## Suggested next move

- Promote the top recurring lemma into a standalone theorem if not already tested.
