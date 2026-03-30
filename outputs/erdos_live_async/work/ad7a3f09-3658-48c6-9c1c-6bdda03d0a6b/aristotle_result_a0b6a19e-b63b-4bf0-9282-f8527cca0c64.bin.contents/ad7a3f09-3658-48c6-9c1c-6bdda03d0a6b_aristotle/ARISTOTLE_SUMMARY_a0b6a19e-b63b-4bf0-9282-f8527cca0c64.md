# Summary of changes
## Summary

### Reusable Invariant: Superset Monotonicity of d-Completeness

The **monotonicity principle** (`IsDComplete_mono`) was identified as the reusable invariant explaining the recurring "unknown" signal. It states:

> If `A ⊆ B` and `A` is d-complete, then `B` is d-complete.

This is the structural core connecting different d-completeness results across the Erdős problem family:
1. **Reduction**: To prove d-completeness for `PowTripleSet a b c`, it suffices to prove it for any subset.
2. **Composability**: Different proof strategies (staircase antichains, cross-family constructions, scaling) establish d-completeness for overlapping subsets; monotonicity combines them.
3. **Invariance**: Enlarging the pool of summands preserves d-completeness — it can only help.

### Proved Lemmas (all sorry-free)

The following lemmas were formally proved in `Main.lean`:

- **`IsDComplete_mono`** — The monotonicity principle (superset preserves d-completeness)
- **`one_mem_PowTripleSet`** — `1 ∈ PowTripleSet a b c`
- **`mul_a_mem_PowTripleSet`**, **`mul_b_mem_PowTripleSet`**, **`mul_c_mem_PowTripleSet`** — Closure under generator multiplication
- **`pow_a_mem`**, **`pow_b_mem`**, **`pow_c_mem`** — Powers of generators belong to the set
- **`IsDivisionAntichain_singleton`**, **`IsDivisionAntichain_empty`** — Basic antichain facts
- **`PowTripleSet_dvd_iff`** — Divisibility in the semigroup corresponds to componentwise ≤ on exponent triples (i.e., `a^i₁·b^j₁·c^k₁ ∣ a^i₂·b^j₂·c^k₂ ↔ i₁≤i₂ ∧ j₁≤j₂ ∧ k₁≤k₂`)
- **`representable_scale_a`** — Scaling closure: if `m` is representable as an antichain sum, then `a·m` is also representable

### Remaining Sorry

The main theorem `erdos_123_d_complete_sequences` (Erdős Problem 123) retains one `sorry`. This is a deep result from additive number theory stating that for pairwise coprime `a, b, c ≥ 2`, the multiplicative semigroup `{a^i · b^j · c^k}` is d-complete. The proof requires showing that antichain subset sums from level-`L` elements eventually cover long enough intervals, combined with the scaling bootstrap — machinery that goes beyond what could be fully formalized in this session. The theorem statement, structural infrastructure, and proof strategy are all documented in the file.