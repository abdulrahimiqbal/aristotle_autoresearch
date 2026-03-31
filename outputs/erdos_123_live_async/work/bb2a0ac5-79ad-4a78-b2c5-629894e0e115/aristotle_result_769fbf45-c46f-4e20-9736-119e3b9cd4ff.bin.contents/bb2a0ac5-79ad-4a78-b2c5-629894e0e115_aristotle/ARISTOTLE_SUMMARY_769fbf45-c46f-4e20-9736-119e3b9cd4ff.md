# Summary of changes
## Summary

All sorries have been filled except for the final open conjecture (`erdos_123_d_complete_sequences`), which is Erdős Problem 123 — a known open problem in additive number theory.

### Adversarial Witness: `PowTripleSet 2 2 2` exposes the coprimality hypotheses

The core contribution is a complete, machine-verified proof chain showing that the pairwise coprimality hypotheses in the Erdős-123 conjecture are **necessary**:

1. **`not_pairwiseCoprime_222`** — The triple (2, 2, 2) fails pairwise coprimality since gcd(2,2) = 2 ≠ 1.

2. **`powTripleSet_222_subset_powers_of_two`** / **`powers_of_two_subset_powTripleSet_222`** — `PowTripleSet 2 2 2 = {2^n : n ∈ ℕ}`. When coprimality fails and all three bases coincide, the multiplicative semigroup collapses to powers of a single prime.

3. **`pow_two_dvd_of_ne`** — Distinct powers of 2 are totally ordered by divisibility: if `a = 2^m ≠ 2^n = b`, then `a ∣ b` or `b ∣ a`.

4. **`antichain_powers_of_two_card_le_one`** — Any division antichain drawn from powers of 2 has at most one element (since any two distinct elements are comparable by divisibility).

5. **`antichain_sum_of_powTripleSet_222`** — Consequently, any antichain sum from `PowTripleSet 2 2 2` is either 0 (empty antichain) or a single power of 2.

6. **`not_d_complete_powTripleSet_222`** — Since arbitrarily large numbers (e.g., `3 · 2^N`) are neither 0 nor powers of 2, `PowTripleSet 2 2 2` is **not** d-complete. This is the main adversarial result.

### Discovery: Which special cases transfer?

The obstruction is structural: when coprimality fails, the multiplicative semigroup `{a^i · b^j · c^k}` degenerates — its elements become totally ordered by divisibility, killing the antichain mechanism. The verified examples `pairwiseCoprime_2_3_5` and `pairwiseCoprime_2_3_7` confirm that triples like (2,3,5) and (2,3,7) satisfy the coprimality precondition, so any progress on these special cases (which have richer divisibility structure) would transfer to the general conjecture once reformulated in terms of the non-degeneracy of the divisibility partial order on the semigroup.

### Remaining sorry

`erdos_123_d_complete_sequences` (the full Erdős Problem 123 conjecture) remains as `sorry` — this is an open problem in mathematics.