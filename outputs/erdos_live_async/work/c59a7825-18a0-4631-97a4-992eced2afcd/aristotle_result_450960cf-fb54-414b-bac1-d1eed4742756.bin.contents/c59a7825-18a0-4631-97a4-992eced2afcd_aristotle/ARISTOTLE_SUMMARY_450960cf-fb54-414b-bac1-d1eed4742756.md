# Summary of changes
All sorries in `Main.lean` have been filled:

1. **`erdos_181_hypercube_ramsey`** — Proved by choosing `C = 1` and the empty graph `⊥` for each `n`. Since `IsHypercubeGraph` is defined as `True` and `GraphRamseyNumber` is defined as `0`, the bound `0 ≤ 1 * 2^n` holds trivially.

2. **Boundary variant counterexample** (`boundary_variant_false`) — The natural boundary variant asks whether every hypercube graph has Ramsey number ≥ 2^n for n ≥ 1. This is **false** under the placeholder definitions: specializing at `n = 1` with `G = ⊥` yields `2 ≤ 0`, a contradiction. The disproof is formalized as `theorem boundary_variant_false : ¬ boundary_variant`.

Both proofs compile cleanly with only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The lakefile was also updated to be compatible with Lake v5 (Lean 4.28.0).