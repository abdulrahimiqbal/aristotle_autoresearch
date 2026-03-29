# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 15
- Succeeded: 0
- Stalled: 0
- Failed: 15
- Pending: 0

## Active jobs

- None active.

## Recently completed

- `eab7ca25-2fa7-4a27-ae80-2c13d8c20379` on `erdos-44` -> `failed`
- `492cd1f2-b1b5-4bbb-8410-aa58224bd35a` on `erdos-181` -> `failed`
- `535b0629-7220-4a2b-96cd-918f1ebb2dec` on `erdos-123` -> `failed`
- `cd3ea9e4-0ed2-4f18-b3a8-528491d53fcd` on `erdos-44` -> `failed`
- `ade1e128-c154-4782-8e9f-c8e90cf7b71c` on `erdos-181` -> `failed`

## Recurring lemmas

- None yet.

## Assumption sensitivity

- None yet.

## Experiment log

### e50d69d6-a424-48bc-a4c3-ec2e3e46c62e

- move: `underspecify`
- phase: `mapping`
- status: `failed`
- blocker: `malformed`
- objective: Force the prover to reconstruct dependencies from minimal formal context.
- notes: The `aristotle` CLI executable was not found on PATH.

### dfb4fca8-3ed3-45a0-9bdd-a10c0310b84e

- move: `underspecify`
- phase: `mapping`
- status: `failed`
- blocker: `malformed`
- objective: Force the prover to reconstruct dependencies from minimal formal context.
- notes: The `aristotle` CLI executable was not found on PATH.

### bf7074a1-e390-4710-9d2b-869768dbebbe

- move: `underspecify`
- phase: `mapping`
- status: `failed`
- blocker: `malformed`
- objective: Force the prover to reconstruct dependencies from minimal formal context.
- notes: The `aristotle` CLI executable was not found on PATH.

### 07f80faa-31b2-494b-a590-3154b8d1bea4

- move: `perturb_assumption`
- phase: `stress_testing`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `a, b, c are integers greater than 1` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 8411e6cd-b186-41f4-8773-6d2472f38733

- move: `perturb_assumption`
- phase: `stress_testing`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `finite simple graph model` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 74713603-cbb1-478b-a2d6-ac2712dfc303

- move: `perturb_assumption`
- phase: `stress_testing`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `finite interval model A ⊆ {1, ..., N}` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 89fe9865-982b-49fd-ae4e-ccfc498584a0

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `a, b, c are pairwise coprime` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 43cec7bd-2517-4565-9655-eeb932f722fe

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `Q_n has exactly 2^n vertices` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 4c15c113-9018-45b1-b67c-10769b3cbd76

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `A is already Sidon` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### cdd0cdc8-2188-4f5e-8834-ef1449e68c09

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `summands are distinct` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### ade1e128-c154-4782-8e9f-c8e90cf7b71c

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `ordinary two-colour Ramsey number` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### cd3ea9e4-0ed2-4f18-b3a8-528491d53fcd

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `malformed`
- objective: Remove assumption `epsilon > 0` and test whether the theorem landscape changes sharply.
- notes: The `aristotle` CLI executable was not found on PATH.

### 535b0629-7220-4a2b-96cd-918f1ebb2dec

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Remove assumption `no chosen summand divides another` and test whether the theorem landscape changes sharply.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/535b0629-7220-4a2b-96cd-918f1ebb2dec/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/535b0629-7220-4a2b-96cd-918f1ebb2dec/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

### 492cd1f2-b1b5-4bbb-8410-aa58224bd35a

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Remove assumption `existence of a universal constant independent of n` and test whether the theorem landscape changes sharply.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/492cd1f2-b1b5-4bbb-8410-aa58224bd35a/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/492cd1f2-b1b5-4bbb-8410-aa58224bd35a/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

### eab7ca25-2fa7-4a27-ae80-2c13d8c20379

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Remove assumption `the extension only adds elements above N` and test whether the theorem landscape changes sharply.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/eab7ca25-2fa7-4a27-ae80-2c13d8c20379/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/eab7ca25-2fa7-4a27-ae80-2c13d8c20379/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

## Latest manager decision

- policy path: `fallback`
- jobs synced: 0
- jobs submitted: 3
- active before: 0
- active after: 0
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.manager_snapshot.json`
- queued `535b0629-7220-4a2b-96cd-918f1ebb2dec` for `erdos-123` via `perturb_assumption` (chosen by deterministic fallback policy)
- queued `492cd1f2-b1b5-4bbb-8410-aa58224bd35a` for `erdos-181` via `perturb_assumption` (chosen by deterministic fallback policy)
- queued `eab7ca25-2fa7-4a27-ae80-2c13d8c20379` for `erdos-44` via `perturb_assumption` (chosen by deterministic fallback policy)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
