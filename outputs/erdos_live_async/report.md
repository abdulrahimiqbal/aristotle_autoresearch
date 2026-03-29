# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 6
- Succeeded: 0
- Stalled: 0
- Failed: 6
- Pending: 0

## Active jobs

- None active.

## Recently completed

- `74713603-cbb1-478b-a2d6-ac2712dfc303` on `erdos-44` -> `failed`
- `8411e6cd-b186-41f4-8773-6d2472f38733` on `erdos-181` -> `failed`
- `07f80faa-31b2-494b-a590-3154b8d1bea4` on `erdos-123` -> `failed`
- `bf7074a1-e390-4710-9d2b-869768dbebbe` on `erdos-44` -> `failed`
- `dfb4fca8-3ed3-45a0-9bdd-a10c0310b84e` on `erdos-181` -> `failed`

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

## Latest manager decision

- policy path: `fallback`
- jobs synced: 0
- jobs submitted: 3
- active before: 0
- active after: 0
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.manager_snapshot.json`
- queued `07f80faa-31b2-494b-a590-3154b8d1bea4` for `erdos-123` via `perturb_assumption` (chosen by deterministic fallback policy)
- queued `8411e6cd-b186-41f4-8773-6d2472f38733` for `erdos-181` via `perturb_assumption` (chosen by deterministic fallback policy)
- queued `74713603-cbb1-478b-a2d6-ac2712dfc303` for `erdos-44` via `perturb_assumption` (chosen by deterministic fallback policy)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
