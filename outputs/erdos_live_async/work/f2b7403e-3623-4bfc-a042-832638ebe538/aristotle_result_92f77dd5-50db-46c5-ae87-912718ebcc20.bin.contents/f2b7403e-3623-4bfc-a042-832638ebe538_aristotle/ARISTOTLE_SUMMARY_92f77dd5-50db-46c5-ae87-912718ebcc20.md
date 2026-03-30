# Summary of changes
## Falsifying witness for the most fragile variant of Erdős Problem 123

The project contained a formalization of Erdős Problem 123: for pairwise coprime `a, b, c > 1`, the set `{a^i · b^j · c^k}` is d-complete (all sufficiently large integers are representable as antichain sums from the set).

### Most fragile variant identified

The **most fragile variant** is the statement with the `PairwiseCoprime3` hypothesis removed — asserting d-completeness for *all* triples `a, b, c > 1` regardless of coprimality.

### Falsifying witness: `a = b = c = 2`

I constructed and formally verified a counterexample in `Main.lean` showing this variant is false. The proof chain:

1. **`powTripleSet_222_eq`**: `PowTripleSet 2 2 2 = {2^n | n ∈ ℕ}` — the set degenerates to powers of 2.
2. **`pow2_divides_of_ne`**: Any two distinct powers of 2 satisfy a divisibility relation.
3. **`antichain_pow2_card_le_one`**: A division antichain drawn from powers of 2 has at most one element.
4. **`antichain_sum_pow2`**: Any antichain sum from the set is either 0 or a power of 2.
5. **`three_not_antichain_sum`**: 3 is not representable as an antichain sum.
6. **`fragile_variant_false`**: The variant without coprimality is false — for any threshold `N`, the odd number `2N + 3 ≥ N` is not representable (it's neither 0 nor a power of 2).

All counterexample lemmas are fully proved (no `sorry`), using only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The original problem stub `erdos_123_d_complete_sequences` retains its `sorry` as it is an open problem.