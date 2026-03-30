# Summary of changes
## Falsifying Witness for the Most Fragile Variant

### Identified fragile variant
The most fragile variant of the Erdős Problem 123 statement is obtained by **dropping the `PairwiseCoprime3` hypothesis**. Without pairwise coprimality, the generators can share a common prime factor, collapsing the multiplicative semigroup into a totally ordered divisibility chain — which destroys the division-antichain representability needed for d-completeness.

### Concrete counterexample: `(a, b, c) = (2, 4, 8)`

The proof proceeds through five fully verified lemmas in `Main.lean`:

1. **`powTripleSet_248_subset_pow2`** — Every element of `PowTripleSet 2 4 8` is a power of 2, since `2^i · 4^j · 8^k = 2^(i+2j+3k)`.

2. **`pow2_div_of_ne`** — Among any two distinct powers of 2, the smaller always divides the larger.

3. **`antichain_pow2_card_le_one`** — Any `IsDivisionAntichain` subset of powers of 2 has at most one element (immediate from the previous lemma).

4. **`antichain_sum_pow2`** — An antichain sum from powers of 2 is either 0 or a single power of 2.

5. **`odd_ge3_not_zero_or_pow2`** — No odd number ≥ 3 is 0 or a power of 2.

These combine into:

- **`fragile_variant_counterexample`**: `¬ IsDComplete (PowTripleSet 2 4 8)` — for any bound N, the odd number `2N+3` is unreachable as an antichain sum.

- **`erdos_123_no_coprime_false`**: The universal statement without coprimality is false, since `(2, 4, 8)` satisfies `1 < a, 1 < b, 1 < c` but fails d-completeness.

All proofs compile cleanly and depend only on standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The original open conjecture stub (`erdos_123_d_complete_sequences`, which includes the coprimality hypothesis) is preserved with its `sorry`.