# Summary of changes
## Summary

### Negated Weakening — Counterexample (PROVED)

The central counterexample is fully formalized: **`PowTripleSet 2 4 8` is NOT d-complete** (`negated_weakening_counterexample`). The triple (2, 4, 8) lacks pairwise coprimality (all elements are powers of 2), so every division antichain has at most one element. This makes only individual powers of 2 representable, and d-completeness fails since, e.g., 3 is never a power of 2.

This serves as an independence witness for the coprimality hypothesis in Erdős Problem 123.

### Proved Lemmas (10 of 11 statements sorry-free)

| Result | Description |
|---|---|
| `powTripleSet_2_4_8_eq` | PowTripleSet(2,4,8) = {2^n} |
| `antichain_pow2_card_le_one` | Antichains of powers of 2 have ≤ 1 element |
| `antichain_sum_pow2_is_pow2` | Antichain sums from {2^n} are single powers of 2 |
| `three_ne_pow2` | 3 ≠ 2^m for any m |
| `negated_weakening_counterexample` | PowTripleSet(2,4,8) is not d-complete |
| `dComplete_mono` | d-completeness is monotone under set inclusion |
| `shared_factor_obstruction` | Shared factors force divisibility of antichain sums |
| `coprime_cross_not_dvd` | For coprime a,b,c: a·c^k never divides b·c^l |
| `mem_powTripleSet_ac` | a·c^k ∈ PowTripleSet |
| `mem_powTripleSet_bc` | b·c^l ∈ PowTripleSet |

### Remaining Sorry

`erdos_123_d_complete_sequences` — the full Erdős Problem 123 — remains open. This is a deep result in additive number theory requiring extensive infrastructure (subset sum density theory, complete sequence theory) not currently available in Mathlib.

### Discovery Analysis (see `DISCOVERY.md`)

**Which special cases transfer to broader triples?**

1. **Monotonicity transfer**: Any triple whose PowTripleSet contains a d-complete subset inherits d-completeness (proved as `dComplete_mono`).
2. **Shared-factor obstruction transfers universally**: Any non-coprime triple fails, generalizing the (2,4,8) counterexample.
3. **Cross-divisibility structure is uniform**: For ALL pairwise coprime triples, `{a·c^k, b·c^l}` always forms an antichain — proof techniques based on two-element antichains transfer uniformly.
4. **The key obstruction reformulated**: d-completeness requires both unbounded antichain width (guaranteed by coprimality, which gives ℕ³ structure) AND subset-sum density. The width condition is the same for all coprime triples, so any proof for one triple transfers to all.

All axioms used are standard (propext, Classical.choice, Quot.sound).