# Summary of changes
## Summary

### Sorries filled
All provable sorries have been filled. Five theorems/lemmas are now fully machine-verified:

1. **`powTripleSet_248_subset_pow2`** — Every element of `PowTripleSet 2 4 8` is a power of 2, since `2^i · 4^j · 8^k = 2^(i+2j+3k)`.

2. **`pow2_dvd_of_ne`** — Among distinct powers of 2, one always divides the other (by comparing exponents).

3. **`antichain_pow2_card_le_one`** — Any divisibility antichain of powers of 2 has at most one element (using the above).

4. **`three_not_pow2`** — 3 is not a power of 2.

5. **`not_d_complete_248`** — **The main counterexample:** `PowTripleSet 2 4 8` is *not* d-complete. The proof shows that for any threshold `x`, the odd number `2x+3` has no antichain-sum representation from this set.

### Remaining sorry
The one remaining `sorry` is `erdos_123_d_complete_sequences` — this is **Erdős Problem 123**, an open conjecture in additive combinatorics. No proof or disproof is known.

### Discovery question answer

**Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?**

The sharpest witness is **(a, b, c) = (2, 4, 8)**, formally proved as `not_d_complete_248`. The mechanism:

- **Interval-style coverage works:** Every positive integer is a sum of *distinct* powers of 2 (binary representation), so the set `{2^n}` has excellent additive coverage of ℕ.

- **The antichain upgrade fails completely:** Since any two distinct powers of 2 satisfy a divisibility relation (the smaller always divides the larger), every divisibility antichain from this set is a singleton. The only achievable antichain sums are individual powers of 2 — a vanishingly sparse subset of ℕ.

- **The boundary is pairwise coprimality:** The triple (2, 4, 8) fails `PairwiseCoprime3` because all generators share the base 2. This collapses the three-dimensional exponent structure `(i, j, k)` into a one-dimensional chain `2^m`, destroying the combinatorial freedom needed to build antichains. The Erdős conjecture hypothesizes that pairwise coprimality is exactly the condition that prevents this collapse.

All proofs compile cleanly and use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).