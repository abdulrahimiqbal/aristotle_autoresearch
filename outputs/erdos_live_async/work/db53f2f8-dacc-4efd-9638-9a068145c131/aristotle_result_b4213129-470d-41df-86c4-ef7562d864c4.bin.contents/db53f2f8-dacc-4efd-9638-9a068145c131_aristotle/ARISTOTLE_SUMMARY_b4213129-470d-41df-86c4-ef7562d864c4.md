# Summary of changes
## Summary

### What was accomplished

**Proved 7 out of 9 declarations** in `Main.lean`. The two remaining `sorry`s correspond to genuinely open problems in additive combinatorics (Erdős Problem 44 and its boundary variant).

### Proved theorems

1. **`IsSidonFinset.subset`** — Sidon property is inherited by subsets
2. **`isSidonFinset_empty`** — The empty set is Sidon
3. **`isSidonFinset_singleton`** — Singletons are Sidon
4. **`union_empty_sidon`** — A ∪ ∅ preserves Sidon
5. **`erdos_44_large_epsilon`** — The main theorem for ε ≥ 1 (trivial case: (1−ε) ≤ 0 makes the density requirement vacuous)
6. **`erdos_44_large_A`** — The main theorem when |A|² ≥ N (the set A is already large enough; take B = ∅ and M = |A|²)
7. **`boundary_implies_main`** — The boundary variant (ε = 0) implies the main statement for all ε > 0

### Remaining sorries (open problems)

- **`erdos_44_sidon_extension`** — The full Erdős Problem 44. This requires constructing Sidon extensions of prescribed near-optimal density, which demands algebraic constructions (Singer difference sets) or probabilistic arguments not currently available in Mathlib.
- **`erdos_44_boundary_variant`** — The ε = 0 boundary variant, which is strictly stronger.

### Boundary variant analysis

The boundary variant replaces `(1 − ε)√M` with `√M`, demanding exact coefficient 1. It is strictly stronger because M₀ cannot depend on ε (whereas M_ε → ∞ as ε → 0⁺ is permitted in the main statement).

**Counterexample search**: Exhaustive backtracking search over all Sidon extensions was conducted for:
- Greedy Sidon sets in [1, N] for N ≤ 10, with M ≤ 80 (optimal via branch-and-bound)
- A = {1,2,5}, {1,2,3,5,8}, {1,2,3}, and other initial sets

**No counterexample was found.** In all tested cases, the optimal Sidon extension exceeds √M. The greedy (non-optimal) algorithm does fall below √M for larger M (e.g., ratio 0.72 at M = 5000), but exhaustive search confirms the optimal always exceeds √M in the tested range.

This is consistent with Singer constructions yielding Sidon sets of size q + 1 > √(q² + q + 1), providing a structural surplus of ~M^{1/4} elements above √M. The boundary variant appears to be **true** but remains unproved. The relationship `boundary_implies_main` is formally verified, confirming that proving the boundary variant would resolve the main conjecture.