# Summary of changes
## Counterexample to the Most Fragile Variant of Erdős Problem 123

### Identification of the fragile hypothesis

The statement `erdos_123_d_complete_sequences` asserts that `PowTripleSet a b c` is d-complete whenever `a, b, c > 1` are **pairwise coprime**. The **pairwise coprimality** condition (`PairwiseCoprime3`) is the most fragile hypothesis — dropping it immediately breaks the conclusion.

### Falsifying witness: `a = 2, b = 4, c = 8`

**Key insight:** `PowTripleSet 2 4 8 = {2^n | n ∈ ℕ}`, since `2^i · 4^j · 8^k = 2^(i+2j+3k)`. Among powers of 2, any two distinct elements satisfy divisibility (the smaller divides the larger), so every `IsDivisionAntichain` subset is a singleton or empty. The only achievable antichain sums are 0 and individual powers of 2 — all odd numbers ≥ 3 are unrepresentable, refuting d-completeness.

### What was proved in Lean (all sorry-free, verified with `lean_build`)

In `Main.lean`:

1. **`PowTripleSet_248_subset_pow2`** — Every element of `PowTripleSet 2 4 8` is a power of 2.
2. **`antichain_pow2_card_le_one`** — Among powers of 2, any division-antichain has at most one element.
3. **`three_ne_pow2`** — 3 is not a power of 2.
4. **`three_not_antichain_sum_in_248`** — 3 has no antichain sum representation in `PowTripleSet 2 4 8`.
5. **`not_d_complete_248`** — `PowTripleSet 2 4 8` is not d-complete (uses arbitrarily large odd counterexamples `2N+3`).
6. **`erdos_123_fragile_variant_is_false`** — The variant of the conjecture *without* pairwise coprimality is **false**.

The only remaining `sorry` is the original open conjecture `erdos_123_d_complete_sequences`, which is the actual Erdős Problem 123. All axioms used are standard (`propext`, `Classical.choice`, `Quot.sound`).