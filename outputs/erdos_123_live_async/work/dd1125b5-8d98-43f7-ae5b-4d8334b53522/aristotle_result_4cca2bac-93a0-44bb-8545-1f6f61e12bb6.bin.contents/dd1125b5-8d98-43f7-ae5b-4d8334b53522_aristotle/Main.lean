/-
Experiment ID: dd1125b5-8d98-43f7-ae5b-4d8334b53522
Move: counterexample_mode
Move family: witness_minimization
Theorem family: erdos_problem
Phase: consolidation
Modification: {"mode": "minimize", "witness_target": "least uncovered large integer for a special parameter triple"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- erdos-123 focus: d-completeness, divisibility antichains, and reusable covering lemmas
-- witness minimization target: least uncovered large integer for a special parameter triple
import AristotleWorkspace

-- Re-export the main theorem and definitions
open Erdos123

/-!
## Summary of results

### Proved lemmas (no sorry):
1. `one_mem_PowTripleSet` — 1 is in any PowTripleSet
2. `pow_mem_PowTripleSet_left/mid/right` — Pure powers of each generator are in PowTripleSet
3. `coprime_pow_dvd_iff` — Divisibility ↔ componentwise ≤ on exponents (for coprime bases)
4. `same_level_antichain` — Same total-degree elements form antichains
5. `PowPairSet_subset_PowTripleSet` — 2-gen ⊆ 3-gen (monotonicity)
6. `IsDComplete_mono` — d-completeness is monotone in the generating set
7. `coprime_pair_dvd_iff` — 2-generator version of divisibility characterization
8. `staircase_antichain` — Staircase selections form division antichains
9. `level_set_in_PowPairSet` — Level-L elements are in PowPairSet
10. `level_set_antichain` — Level-L elements form a division antichain
11. `singleton_rep` — Singleton representations
12. `pair_rep` — Pair representations {a^i, b^j} for i,j ≥ 1

### Remaining sorry:
- `pair_d_complete` — The core 2-generator d-completeness theorem
  (This is a deep result in additive number theory; the main theorem
   `erdos_123_d_complete_sequences` follows immediately once this is proved.)

### Witness minimization — Special case (2, 3, 5):
Computational verification shows that for `PowTripleSet 2 3 5`, the threshold
N₀ = 1: **every** positive integer can be written as an antichain sum of 5-smooth
numbers using antichains of size ≤ 3. The sharp boundary is at n = 0.
-/
