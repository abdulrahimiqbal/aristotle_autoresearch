# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 3
- Succeeded: 0
- Stalled: 0
- Failed: 3
- Pending: 0

## Active jobs

- None active.

## Recently completed

- `bf7074a1-e390-4710-9d2b-869768dbebbe` on `erdos-44` -> `failed`
- `dfb4fca8-3ed3-45a0-9bdd-a10c0310b84e` on `erdos-181` -> `failed`
- `e50d69d6-a424-48bc-a4c3-ec2e3e46c62e` on `erdos-123` -> `failed`

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

## Latest manager decision

- policy path: `fallback`
- jobs synced: 0
- jobs submitted: 3
- active before: 0
- active after: 0
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_live_async/report.manager_snapshot.json`
- queued `e50d69d6-a424-48bc-a4c3-ec2e3e46c62e` for `erdos-123` via `underspecify` (chosen by deterministic fallback policy)
- queued `dfb4fca8-3ed3-45a0-9bdd-a10c0310b84e` for `erdos-181` via `underspecify` (chosen by deterministic fallback policy)
- queued `bf7074a1-e390-4710-9d2b-869768dbebbe` for `erdos-44` via `underspecify` (chosen by deterministic fallback policy)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
