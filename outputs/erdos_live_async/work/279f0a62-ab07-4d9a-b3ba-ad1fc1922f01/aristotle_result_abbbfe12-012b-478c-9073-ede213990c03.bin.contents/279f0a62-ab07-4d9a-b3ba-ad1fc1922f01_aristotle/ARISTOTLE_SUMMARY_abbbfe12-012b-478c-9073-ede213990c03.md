# Summary of changes
## Falsifying Witness for the Most Fragile Variant of Erdős Problem 123

### Identified fragile hypothesis
The **most fragile condition** in `erdos_123_d_complete_sequences` is **pairwise coprimality** (`PairwiseCoprime3 a b c`). Dropping it while keeping `1 < a`, `1 < b`, `1 < c` immediately breaks the conclusion.

### Counterexample: `(a, b, c) = (2, 4, 8)`

All three bases exceed 1, but `gcd(2, 4) = 2 ≠ 1`, so pairwise coprimality fails. The generated semigroup collapses:

```
PowTripleSet 2 4 8 = {2^i · 4^j · 8^k} = {2^(i + 2j + 3k)} = {2^n : n ≥ 0}
```

This is a **totally ordered** set under divisibility (`2^a ∣ 2^b ⟺ a ≤ b`), so every division-antichain has at most one element. The only achievable antichain-sums are individual powers of 2. Most integers (e.g., 3, 5, 6, 7, …) are never representable, so `IsDComplete` fails.

### Formalized in `Main.lean`

Four fully machine-verified lemmas building up to the main result:

1. **`powTripleSet_2_4_8_eq`** — `PowTripleSet 2 4 8 = {n | ∃ m, n = 2^m}`
2. **`antichain_pow2_subsingleton`** — Any division-antichain of powers of 2 has ≤ 1 element
3. **`three_ne_pow2`** — `3 ≠ 2^m` for all `m`
4. **`three_not_antichain_sum_of_pow2`** — 3 has no antichain-sum representation from `PowTripleSet 2 4 8`
5. **`fragile_variant_false`** — The variant without coprimality is **false** (`¬ FragileVariant`)

All proofs compile with only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The original `erdos_123_d_complete_sequences` (the actual open problem) is preserved with its `sorry`.