# Summary of changes
## Counterexample for the Most Fragile Variant of Erdős Problem 123

I identified **pairwise coprimality** (`PairwiseCoprime3 a b c`) as the most fragile hypothesis in the d-completeness theorem. Dropping it causes the theorem to fail dramatically, and I formalized a complete machine-verified proof of this failure.

### Witness: `a = b = c = 2`

When all three generators equal 2, `PowTripleSet 2 2 2 = {2^m | m ∈ ℕ}` (all powers of 2). The key insight is that powers of 2 are **totally ordered** by divisibility (`2^a ∣ 2^b ↔ a ≤ b`), so any division antichain drawn from this set has at most one element. Consequently, the only representable numbers are 0 (empty sum) and powers of 2 themselves. Since odd numbers ≥ 3 are neither 0 nor powers of 2, infinitely many numbers have no antichain-sum representation — hence `IsDComplete` fails.

### Proof Structure (all fully verified, no sorry)

1. **`powTripleSet_222_eq`** — `PowTripleSet 2 2 2 = {n | ∃ m, n = 2^m}`: collapse three identical generators into one.
2. **`antichain_powers_of_two_singleton`** — Any division antichain of powers of 2 has `card ≤ 1`: powers of 2 are totally ordered by divisibility.
3. **`singleton_sum_is_pow2`** — An antichain sum from powers of 2 is either 0 or itself a power of 2.
4. **`three_ne_pow2`** — `3 ≠ 2^m` for all `m`.
5. **`three_not_representable`** — 3 has no antichain-sum representation from `PowTripleSet 2 2 2`.
6. **`fragile_variant_coprimality`** — `¬ IsDComplete (PowTripleSet 2 2 2)`: for arbitrarily large `n` (specifically `2x + 3`, which is always odd ≥ 3), no representation exists.

The proof uses only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The original open problem `erdos_123_d_complete_sequences` remains as `sorry`, as expected.