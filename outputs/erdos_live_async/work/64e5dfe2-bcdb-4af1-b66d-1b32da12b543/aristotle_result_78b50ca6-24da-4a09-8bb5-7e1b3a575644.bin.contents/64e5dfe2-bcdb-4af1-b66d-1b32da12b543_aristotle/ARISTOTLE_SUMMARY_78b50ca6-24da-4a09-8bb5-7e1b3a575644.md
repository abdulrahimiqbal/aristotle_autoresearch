# Summary of changes
## Summary

### Sorries filled

All provable `sorry`s have been eliminated. The following lemmas and theorems are now fully proved (verified by `#print axioms` — no `sorryAx`):

- **`isSidonFinset_empty`**: The empty set is vacuously Sidon.
- **`IsSidonFinset.subset`**: Subsets of Sidon sets are Sidon.
- **`sidon_diff_injective`**: Distinct pairs in a Sidon set yield distinct differences.
- **`sidon_pairs_bound`**: For a Sidon set A ⊆ [1, M], the counting bound |A|·(|A|−1) ≤ 2·(M−1) holds. Proved by constructing an injection from ordered pairs with a < b to {1,…,M−1} via the difference map.
- **`sidon_card_lt_two_sqrt`**: Any Sidon set in [1, M] has strictly fewer than 2√M elements. Derived from `sidon_pairs_bound` by contradiction.
- **`erdos_44_boundary_variant_false`**: **The boundary variant is FALSE** (see below).

### Boundary variant counterexample

The **boundary variant** replaces the factor `(1 − ε)` with `(1 + ε)` in the Erdős Problem 44 statement, asking whether Sidon sets can be extended to achieve *super-√M* density. This is formally disproved in `erdos_44_boundary_variant_false`.

**Key idea**: Instantiate ε = 1. Then (1 + ε)√M = 2√M. For any proposed threshold Mε, take N = 1 and A = ∅. For any M ≥ max(1, Mε) and any Sidon B ⊆ [2, M], we have B ⊆ [1, M], so by `sidon_card_lt_two_sqrt`, |B| < 2√M. This contradicts the requirement 2√M ≤ |B|.

The proof chain is: distinct-differences injectivity → pair-counting bound → size upper bound → boundary variant refutation.

### Remaining sorry

`erdos_44_sidon_extension` retains its `sorry`. This is an open problem in additive combinatorics (related to Erdős Problem 44): it asserts that *any* Sidon set in [1, N] can be extended to a Sidon set in [1, M] of size ≥ (1−ε)√M. Proving this would require formalizing deep results about Sidon set constructions (Erdős–Turán, Singer difference sets) and extension theorems, which are not currently available in Mathlib.