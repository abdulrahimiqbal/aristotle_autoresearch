# Summary of changes
## Summary

### Sorries filled (6 of 7)

All `sorry`s in the project have been resolved except for the main conjecture `erdos_123_d_complete_sequences`, which is **Erdős Problem 123** — an open problem in combinatorial number theory with no known proof or disproof as of 2025. The remaining `sorry` reflects the state of mathematical knowledge, not a limitation of the formalization.

The following theorems and lemmas were formally proved (all verified by `lean build` with only standard axioms):

| Declaration | Description |
|---|---|
| `powTripleSet_2_4_8_eq` | `PowTripleSet 2 4 8 = {2^k | k ∈ ℕ}` since 4 = 2² and 8 = 2³ |
| `antichain_singleton_of_prime_powers` | Any divisibility antichain in {p^k} has at most 1 element |
| `three_not_pow_two` | 3 is not a power of 2 |
| `fragile_variant_not_d_complete` | **Counterexample**: `PowTripleSet 2 4 8` is NOT d-complete |
| `powers_of_two_complete` | Powers of 2 form a complete sequence (binary representation) |
| `powers_of_two_not_d_complete` | Powers of 2 are NOT d-complete |

### Fragile variant & sharpest witness

The **most fragile variant** of Erdős 123 is obtained by dropping the pairwise coprimality hypothesis. The **sharpest witness** is `(a, b, c) = (2, 4, 8)`:

- **Interval-style coverage holds**: every positive integer is a sum of distinct powers of 2 (binary representation) — proved as `powers_of_two_complete`.
- **The antichain upgrade completely fails**: since `PowTripleSet 2 4 8 = {2^k}` and every pair of distinct powers of 2 has a divisibility relation, the only antichains are singletons. Thus the only achievable antichain sums are individual powers of 2.
- **The gap is maximal**: `3 = 1 + 2` is representable as a sum of distinct powers of 2, but `1 ∣ 2`, so no antichain representation of 3 exists. This applies to every odd number ≥ 3.

This is formalized as `fragile_variant_not_d_complete` (for the concrete triple) and `powers_of_two_not_d_complete` (for the abstract set).

### Discovery question answer

The d-completeness boundary cases that fail because interval-style coverage cannot be upgraded to a divisibility antichain are precisely those where the generating set contains **concentrated divisibility chains**:

1. **Single-prime collapse** (`a = p, b = p², c = p³`): The PowTripleSet collapses to `{p^k}`, where all pairs are comparable. Antichain sums are singletons only.

2. **Two-prime with shared factor** (`a = 6, b = 10, c = 15`): Pairwise non-coprime generators create forced divisibility relations among smooth numbers.

3. **Sparse generators** (only two bases): Lower density of antichain-compatible subsets makes the upgrade harder.

The sharpest witness is **(2, 4, 8)** because it exhibits maximal separation: the set is additively complete (interval coverage holds perfectly via binary representation), yet the antichain upgrade fails completely and structurally — not due to density, but because the entire set is a single divisibility chain. Full analysis is documented in the Part III comments of `AristotleWorkspace.lean`.