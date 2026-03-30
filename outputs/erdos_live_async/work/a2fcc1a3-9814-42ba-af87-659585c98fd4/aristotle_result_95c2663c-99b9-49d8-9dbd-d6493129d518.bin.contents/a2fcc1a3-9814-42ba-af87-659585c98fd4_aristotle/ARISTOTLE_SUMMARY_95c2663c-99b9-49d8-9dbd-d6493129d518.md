# Summary of changes
## Counterexample to the Fragile Variant of Erdős Problem 123

### Identified fragile variant
The **most fragile variant** is obtained by dropping the `PairwiseCoprime3 a b c` hypothesis from the Erdős 123 conjecture — claiming that `PowTripleSet a b c` is `d`-complete for *all* triples with `1 < a, 1 < b, 1 < c`, without requiring pairwise coprimality.

### Falsifying witness: `a = b = c = 2`

The counterexample is fully formalized and machine-verified in `AristotleWorkspace.lean`. The proof proceeds through five helper lemmas:

1. **`powTripleSet_222_subset_pow2`**: Every element of `PowTripleSet 2 2 2` is a power of 2 (since `2^i · 2^j · 2^k = 2^(i+j+k)`).

2. **`pow2_dvd_total`**: Powers of 2 are totally ordered by divisibility (`2^a ∣ 2^b ∨ 2^b ∣ 2^a`).

3. **`antichain_pow2_card_le_one`**: Any divisibility-antichain of powers of 2 has at most one element (consequence of the total order).

4. **`sum_antichain_pow2`**: The sum of such an antichain is either 0 or a single power of 2.

5. **`exists_large_non_pow2`**: For every `N`, there exists `n ≥ N` that is neither 0 nor a power of 2.

These combine into `powTripleSet_222_not_dComplete` (¬ IsDComplete (PowTripleSet 2 2 2)), and the main theorem:

```lean
theorem erdos_123_fragile_variant_false :
    ¬ (∀ a b c : ℕ, 1 < a → 1 < b → 1 < c →
        IsDComplete (PowTripleSet a b c))
```

All proofs compile cleanly with only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). The original `erdos_123_d_complete_sequences` stub (with coprimality hypothesis) is preserved with `sorry` as it is an open/hard conjecture.