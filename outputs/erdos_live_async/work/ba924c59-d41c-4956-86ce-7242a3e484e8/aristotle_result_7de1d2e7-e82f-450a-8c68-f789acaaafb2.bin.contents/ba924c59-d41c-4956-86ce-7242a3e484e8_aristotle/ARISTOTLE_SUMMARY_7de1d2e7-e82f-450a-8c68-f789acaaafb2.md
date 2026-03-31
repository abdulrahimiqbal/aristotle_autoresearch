# Summary of changes
## Summary

### Original Theorem (`erdos_44_sidon_extension`)
This is **Erdős Problem 44**, an open problem in additive combinatorics asserting that any Sidon set in `{1, …, N}` can be extended to a near-optimal Sidon set of size `(1−ε)√M` in a larger interval `{1, …, M}`. The `sorry` remains because this is genuinely unresolved in mathematics.

### Minimal Variant & Counterexample
I defined a **minimal variant** (`erdos_44_minimal_variant`) that strengthens the density exponent from `1/2` to `3/4` — replacing the bound `(1−ε)√M` with `M^(3/4)`. This is the most natural "next step" strengthening of the original conjecture.

**This variant is formally disproved** via `erdos_44_minimal_variant_false`, establishing that the `√M` exponent is essentially tight. The proof proceeds through:

1. **`sidon_card_bound`**: The classical pair-sum counting argument — for a Sidon set `A ⊆ {1,…,N}`, the map `{a,b} ↦ a+b` is injective on multiset pairs, with all sums in `{2,…,2N}`, giving `|A|(|A|+1) ≤ 4N`.

2. **`sidon_card_sq_le`**: Corollary: `|A|² ≤ 4N`.

3. **`sqrt_lt_rpow_three_fourths`**: For `M ≥ 256`, `2√M < M^(3/4)` (equivalent to `M > 16`).

4. **`erdos_44_minimal_variant_false`**: For any proposed threshold `Mε`, take `N = 256 + Mε` and `A = {1}`. For every `M ≥ max(N, Mε) ≥ 256`, any Sidon extension `A ∪ B ⊆ {1,…,M}` satisfies `|A∪B|² ≤ 4M`, hence `|A∪B| ≤ 2√M < M^(3/4)`, contradicting the variant's density requirement.

All helper lemmas (`isSidonFinset_singleton`, `singleton_subset_Icc`, etc.) are fully proved. The project builds cleanly with only the open problem's sorry remaining. All proofs use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).