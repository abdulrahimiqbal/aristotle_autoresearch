# Summary of changes
## Counterexample to the Most Fragile Variant of Erdős Problem 123

The file `Main.lean` contains a formalization of Erdős Problem 123: for pairwise coprime integers a, b, c > 1, the multiplicative semigroup `PowTripleSet a b c = {a^i · b^j · c^k}` is *d-complete* (every sufficiently large integer is an antichain sum from the set).

### Identified fragile variant

The **most fragile variant** drops the `PairwiseCoprime3 a b c` hypothesis. Without coprimality, the statement becomes false.

### Falsifying witness: a = b = c = 2

I created `Counterexample.lean` with a fully machine-verified proof that:

```
theorem erdos_123_fragile_variant_false :
    ¬ (∀ a b c : ℕ, 1 < a → 1 < b → 1 < c →
      IsDComplete (PowTripleSet a b c))
```

**Proof idea:** Setting a = b = c = 2 collapses the triple-power set to `{2^n | n ∈ ℕ}` (powers of 2). Among powers of 2, every pair satisfies a divisibility relation (2^a ∣ 2^b when a ≤ b), so any division-antichain has at most one element. Therefore achievable antichain sums are exactly `{0} ∪ {2^n : n ∈ ℕ}`, which misses all odd numbers ≥ 3.

### Structure of the proof (all sorry-free, verified by `lake build`)

| Lemma | Role |
|-------|------|
| `powTripleSet_222_eq` | PowTripleSet 2 2 2 = {2^n} |
| `antichain_pow2_card_le_one` | Any antichain in {2^n} has ≤ 1 element |
| `sum_of_card_le_one` | Such a finset sums to 0 or its unique element |
| `odd_not_pow2` | Odd numbers ≥ 3 are neither 0 nor powers of 2 |
| `powTripleSet_222_not_dComplete` | PowTripleSet 2 2 2 is not d-complete |
| `erdos_123_fragile_variant_false` | The variant without coprimality is false |

All axioms are standard (`propext`, `Classical.choice`, `Quot.sound`).