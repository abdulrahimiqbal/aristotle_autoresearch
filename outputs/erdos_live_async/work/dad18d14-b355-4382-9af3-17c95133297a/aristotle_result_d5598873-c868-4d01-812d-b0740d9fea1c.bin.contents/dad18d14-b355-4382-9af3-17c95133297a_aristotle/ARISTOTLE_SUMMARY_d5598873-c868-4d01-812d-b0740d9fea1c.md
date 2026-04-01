# Summary of changes
## Summary

### Main theorem (`erdos_44_sidon_extension`)
This is **Erdős Problem 44**, an open problem in additive combinatorics about extending Sidon sets while maintaining near-optimal density proportional to √M. Proving it requires formalizing the Singer/Bose-Chowla construction of dense Sidon sets from finite geometry, which is substantial infrastructure not available in Mathlib. The `sorry` remains — this is a genuine open conjecture.

### Minimal variant counterexample (fully proved)
The **minimal variant** (`erdos_44_minimal_variant`) strengthens the density bound from `(1-ε)·√M` (sub-linear) to `(1-ε)·M` (linear), asking whether Sidon set extensions can achieve linear density. This is **proved false** via a clean counting argument:

1. **`sidon_pairsum_injective`**: The ordered pair-sum map on a Sidon set is injective (direct from the Sidon definition).

2. **`sidon_card_sq_le`**: Any Sidon set A ⊆ [1,M] satisfies |A|² ≤ 4M. This follows because the |A|(|A|+1)/2 distinct pair sums all lie in {2,…,2M}, giving |A|²/2 ≤ 2M−1.

3. **`erdos_44_minimal_variant_false`**: The minimal variant is false. For ε = 1/4, given any Mε, take N = max(Mε, 17) and A = {1}. For any M ≥ N ≥ 17, any Sidon set in [1,M] has at most 2√M elements (by the bound above), but the linear requirement (3/4)·M exceeds 2√M for M ≥ 17. Contradiction.

All proofs compile cleanly and use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).