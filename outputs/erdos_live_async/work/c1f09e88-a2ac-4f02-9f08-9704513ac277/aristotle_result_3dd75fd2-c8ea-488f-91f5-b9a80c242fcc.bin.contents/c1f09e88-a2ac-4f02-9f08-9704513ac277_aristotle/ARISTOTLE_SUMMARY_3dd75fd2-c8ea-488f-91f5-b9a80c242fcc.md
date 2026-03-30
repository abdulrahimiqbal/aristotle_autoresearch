# Summary of changes
## Falsifying Witness for the Most Fragile Variant of Erdős Problem 123

### Identification of the Fragile Variant

The original Erdős Problem 123 conjecture states that for any three **pairwise coprime** integers a, b, c > 1, the multiplicative semigroup {a^i · b^j · c^k} is *d-complete* (every sufficiently large integer is an antichain sum from this set). The **most fragile observed variant** is obtained by dropping the pairwise-coprimality hypothesis — asking whether the conclusion holds for *all* triples a, b, c > 1 regardless of coprimality.

### The Counterexample

**Witness**: (a, b, c) = (2, 4, 8).

These satisfy 1 < a, 1 < b, 1 < c, but gcd(2, 4) = 2 ≠ 1, so pairwise coprimality fails.

**Why it works**: The set {2^i · 4^j · 8^k} = {2^(i+2j+3k)} collapses to {2^n : n ∈ ℕ} — just powers of 2. Since divisibility on powers of 2 is a total order, the only division-antichains are singletons. Therefore, the achievable antichain sums are exactly the powers of 2 themselves — a density-zero set that cannot represent all sufficiently large integers (e.g., 3 is never representable).

### Formal Verification

All results are machine-verified in Lean 4 with Mathlib, with no `sorry`, no custom axioms, and only standard axioms (propext, Classical.choice, Quot.sound). The proof is structured as:

1. **`powTripleSet_2_4_8_eq`**: PowTripleSet 2 4 8 = {2^n : n ∈ ℕ}
2. **`pow2_divides_total`**: Divisibility on powers of 2 is total
3. **`antichain_pow2_card_le_one`**: Division-antichains from {2^n} have ≤ 1 element
4. **`antichain_sum_is_pow2`**: Antichain sums from {2^n} are themselves powers of 2 (or 0)
5. **`three_ne_pow2`**: 3 ≠ 2^m for any m
6. **`no_antichain_sum_3`**: 3 has no antichain sum representation in PowTripleSet 2 4 8
7. **`not_d_complete_2_4_8`**: PowTripleSet 2 4 8 is not d-complete
8. **`erdos_123_fragile_variant_false`**: The non-coprime variant of Erdős 123 is false

### Files

- `AristotleWorkspace/Erdos123.lean` — Original definitions and the (still-open) conjecture statement
- `AristotleWorkspace/FragileVariant.lean` — Complete, sorry-free proof of the counterexample
- `AristotleWorkspace.lean` — Root import file