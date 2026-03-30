# Summary of changes
## Summary

### Open Conjecture (sorry retained)

The theorem `erdos_123_d_complete_sequences` is **Erdős Problem 123**, an open conjecture in combinatorial number theory. It asserts that for pairwise coprime `a, b, c > 1`, the set `{a^i · b^j · c^k}` is d-complete (every sufficiently large integer is an antichain sum from this set). No proof or counterexample is known, so the `sorry` necessarily remains.

**Computational evidence:** Exhaustive backtracking search for `(a,b,c) = (2,3,5)` confirms every integer from 2 to 301 admits an antichain-sum representation — no counterexample was found.

### Counterexample (fully proved, no sorry)

I formalized and proved a counterexample demonstrating that the **pairwise coprimality hypothesis is necessary**. Specifically, `not_d_complete_without_coprimality` proves:

> `¬ IsDComplete (PowTripleSet 2 4 8)`

The proof proceeds via three helper lemmas (all proved):

1. **`powTripleSet_248_eq`**: `PowTripleSet 2 4 8 = {2^m | m : ℕ}` — since `4 = 2²` and `8 = 2³`, every element is a power of 2.
2. **`antichain_pow2_card_le_one`**: Any divisibility antichain of powers of 2 has at most one element (since powers of 2 are totally ordered by divisibility).
3. **`three_ne_pow2`**: `3 ≠ 2^m` for all `m`.

Therefore, any antichain sum from `PowTripleSet 2 4 8` is either 0 or a single power of 2. Since odd non-powers-of-2 (like `2N+3`) exist above any threshold, d-completeness fails.

All proofs use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The project builds successfully with `lake build`.