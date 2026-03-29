# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 21
- Succeeded: 0
- Stalled: 0
- Failed: 18
- Pending: 3

## Active jobs

- `QUEUED`: 3

## Recently completed

- `ace7b855-da46-4293-822e-f736eef6baff` on `erdos-181` -> `failed`
- `6d17890b-1a5c-4a01-8c9c-2be87fa64b68` on `erdos-44` -> `failed`
- `b5d29873-cd24-487d-b51c-9d4f66079862` on `erdos-123` -> `failed`
- `eab7ca25-2fa7-4a27-ae80-2c13d8c20379` on `erdos-44` -> `failed`
- `492cd1f2-b1b5-4bbb-8410-aa58224bd35a` on `erdos-181` -> `failed`

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

### b5d29873-cd24-487d-b51c-9d4f66079862

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Remove assumption `the representation is required only for sufficiently large integers` and test whether the theorem landscape changes sharply.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/b5d29873-cd24-487d-b51c-9d4f66079862/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/b5d29873-cd24-487d-b51c-9d4f66079862/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

### 6d17890b-1a5c-4a01-8c9c-2be87fa64b68

- move: `perturb_assumption`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Remove assumption `target density is measured against M^(1/2)` and test whether the theorem landscape changes sharply.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/6d17890b-1a5c-4a01-8c9c-2be87fa64b68/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/6d17890b-1a5c-4a01-8c9c-2be87fa64b68/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

### ace7b855-da46-4293-822e-f736eef6baff

- move: `reformulate`
- phase: `consolidation`
- status: `failed`
- blocker: `unknown`
- objective: Re-express the conjecture as a there exists C > 0 with R(Q_n) <= C * 2^n for all n.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/ace7b855-da46-4293-822e-f736eef6baff/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/ace7b855-da46-4293-822e-f736eef6baff/aristotle_submit_stderr.txt`
- notes: Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.

### b8a93291-8fe5-46bb-b590-842aaa6c99d1

- move: `reformulate`
- phase: `consolidation`
- status: `submitted`
- blocker: `unknown`
- external job id: `1b2d49f3-d8da-40e5-8d49-7895a1bc3d10`
- external status: `QUEUED`
- objective: Re-express the conjecture as a the set {a^k b^l c^m : k, l, m >= 0} is d-complete.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/b8a93291-8fe5-46bb-b590-842aaa6c99d1/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/b8a93291-8fe5-46bb-b590-842aaa6c99d1/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

### 4a5341f3-55a3-4dd4-9a22-88b11597448f

- move: `reformulate`
- phase: `consolidation`
- status: `submitted`
- blocker: `unknown`
- external job id: `7136ba1e-2909-4d34-a48e-8ac5fcb5795c`
- external status: `QUEUED`
- objective: Re-express the conjecture as a every finite Sidon set can be completed to a near-extremal Sidon set after enlarging the ambient interval.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/4a5341f3-55a3-4dd4-9a22-88b11597448f/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/4a5341f3-55a3-4dd4-9a22-88b11597448f/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

### 7a1440ba-0f7c-49b7-a47e-7d614b3840a6

- move: `counterexample_mode`
- phase: `consolidation`
- status: `submitted`
- blocker: `unknown`
- external job id: `2a66c4e5-db3d-4a9e-ab2b-11b7fab6d4da`
- external status: `QUEUED`
- objective: Seek a falsifying or independence-style witness for the most fragile observed variant.
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/7a1440ba-0f7c-49b7-a47e-7d614b3840a6/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/work/7a1440ba-0f7c-49b7-a47e-7d614b3840a6/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

## Latest manager decision

- policy path: `fallback`
- jobs synced: 0
- jobs submitted: 3
- active before: 0
- active after: 3
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.manager_snapshot.json`
- queued `b8a93291-8fe5-46bb-b590-842aaa6c99d1` for `erdos-123` via `reformulate` (chosen by deterministic fallback policy)
- queued `4a5341f3-55a3-4dd4-9a22-88b11597448f` for `erdos-44` via `reformulate` (chosen by deterministic fallback policy)
- queued `7a1440ba-0f7c-49b7-a47e-7d614b3840a6` for `erdos-181` via `counterexample_mode` (chosen by deterministic fallback policy)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
