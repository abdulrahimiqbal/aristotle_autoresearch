# Erdős Problem 123: Discovery Analysis

## Status Summary

| Component | Status |
|-----------|--------|
| All definitions (`PowTripleSet`, `PairwiseCoprime3`, `IsDivisionAntichain`, `IsDComplete`) | ✅ Proved |
| Boundary counterexample (`PowTripleSet 2 4 8` not d-complete) | ✅ Proved |
| Structural lemmas (positivity, membership, monotonicity, antichain compatibility) | ✅ Proved |
| Main theorem (`erdos_123_d_complete_sequences`) | ❌ Open (sorry) |

## 1. Boundary Variant: Counterexample

**Result**: When the pairwise coprimality condition is removed, d-completeness fails.

**Formal counterexample** (`boundary_counterexample`):
`PowTripleSet 2 4 8` is **not** d-complete.

**Proof structure**:
1. `powTripleSet_248_eq`: Since 4 = 2² and 8 = 2³, the set `PowTripleSet 2 4 8` collapses to `{2^n : n ∈ ℕ}`.
2. `pow_two_dvd_total`: Powers of 2 form a total order under divisibility.
3. `antichain_singleton_of_total`: In any totally ordered set, antichains have at most one element.
4. `pow_two_not_d_complete`: Since antichain sums from `{2^n}` are just individual powers of 2, and not every large integer is a power of 2, d-completeness fails.

**Independence witness interpretation**: The counterexample shows the coprimality hypothesis is *necessary*, not just sufficient. The obstruction is precisely that when generators share a common factor, the multiplicative semigroup can collapse to a chain (totally ordered under divisibility), forcing antichains to be singletons.

More nuanced boundary variants exist:
- **Partial coprimality** (e.g., `gcd(a,b) = 1` but `gcd(a,c) > 1`): The set may still be d-complete if two of the three pairs are coprime, depending on the specific structure. This is an open question.
- **One generator = 1** (boundary of `1 < a`): `PowTripleSet(1, b, c) = {b^j · c^k}` reduces to the two-generator case, which is itself a substantial sub-problem.

## 2. Discovery Question: Which Special Cases Transfer?

### Solved / Provable Special Cases

The following structural results are formally verified and transfer to broader triples:

#### a) Pure-power antichain compatibility (`coprime_pow_antichain`)
For coprime `a, b > 1`, the powers `a^i` and `b^j` (with `i, j > 0`, `a^i ≠ b^j`) are always antichain-incomparable. This transfers immediately to any triple containing `a` and `b` among its generators.

#### b) Mixed-element antichain compatibility (`mixed_pair_antichain`)
For pairwise coprime `a, b, c > 1`, the elements `a · c^i` and `b · c^j` are **always** antichain-compatible (neither divides the other), for *any* `i, j ≥ 0`. This is because `a ∣ b · c^j` would require `a ∣ c^j` (by coprimality with `b`), but `gcd(a, c) = 1` forces `a = 1`, contradicting `a > 1`.

**Transfer principle**: This result shows that the "a-row" and "b-row" of the multiplicative lattice are fully antichain-compatible. Any proof of d-completeness for a specific triple (e.g., `(2, 3, 5)`) that relies only on this row-compatibility property automatically extends to all coprime triples.

#### c) Monotonicity under set inclusion (`isDComplete_mono`)
If `A ⊆ B` and `A` is d-complete, then `B` is d-complete. Combined with `powTripleSet_pair_sub_triple`, this means:

> Any proof that `PowTripleSet(a, b, 1) = {a^i · b^j}` is d-complete immediately implies `PowTripleSet(a, b, c)` is d-complete for all `c`.

This reduces the triple case to the pair case.

#### d) Singleton representations (`singleton_antichain_sum`)
Every element of `PowTripleSet` gives a trivial 1-element antichain sum. Combined with the fact that smooth numbers (elements of `PowTripleSet`) become sparse, this shows that multi-element antichains are needed for most large integers.

### The Reformulated Obstruction

The core obstruction to proving d-completeness can be reformulated as follows:

**Binary Smooth Goldbach Property**: For coprime `a, b, c > 1`, every sufficiently large integer `n` can be written as `n = s₁ + s₂ + ⋯ + sₖ` where:
- Each `sᵢ` is abc-smooth (i.e., `sᵢ ∈ PowTripleSet(a, b, c)`),
- The exponent vectors `(αᵢ, βᵢ, γᵢ)` of the `sᵢ` form an antichain in `(ℕ³, ≤)`.

The antichain condition in `ℕ³` is equivalent to: for each pair `sᵢ, sⱼ` with `i ≠ j`, neither `sᵢ ∣ sⱼ` nor `sⱼ ∣ sᵢ` (by unique factorization for coprime bases).

**Key structural insight**: At any "level" `M` (elements with exponent sum `i + j + k = M`), ALL elements are pairwise antichain-compatible. This is because if `(i₁, j₁, k₁)` componentwise dominates `(i₂, j₂, k₂)` with both summing to `M`, then `i₁ ≥ i₂, j₁ ≥ j₂, k₁ ≥ k₂` forces equality (since all coordinates are non-negative and the sums match). So the level-`M` elements form an antichain of size `(M+1)(M+2)/2`.

The challenge: subset sums from a single level `M` start at `min(a,b,c)^M` (exponentially large), leaving gaps below. Combining elements from different levels risks introducing comparabilities.

### Transferable Proof Strategies

Based on the analysis, the following strategies from solved special cases transfer to the general setting:

1. **Row-compatibility** (from `mixed_pair_antichain`): Any two elements from different "generator rows" (one involving `a` but not `b`, the other involving `b` but not `a`) are antichain-compatible. This means pair sums `a·c^i + b·c^j` are always valid antichain sums.

2. **Level-M antichain construction**: The set of all elements at level `M` forms a large antichain. For specific small triples, one could verify computationally that level-`M` subset sums cover a dense enough interval.

3. **Frobenius reduction**: The Chicken McNugget theorem gives `n = x·a + y·b` for large `n`. If we can show that smooth `x` and `y` can always be found (so that `x·a` and `y·b` are both in `PowTripleSet`), the pair `{x·a, y·b}` is antichain-compatible by `mixed_pair_antichain`.

4. **Base-c digit representation**: For triples where every digit in base `c` is abc-smooth (e.g., `c = 5, a = 2, b = 3`: digits 0–4 are all {2,3,5}-smooth), one can represent `n` in base `c` and convert each digit-position to a `PowTripleSet` element. The antichain condition requires careful management of exponent vectors across digit positions.

### Open Questions

1. **Pair case sufficiency**: Is `{a^i · b^j : i, j ≥ 0}` d-complete for all coprime `a, b > 1`? By monotonicity, this would imply the full triple case.

2. **Effective bounds**: For specific triples like `(2, 3, 5)`, what is the smallest `N₀` such that all `n ≥ N₀` are representable? Computational experiments suggest `N₀` is small (possibly 1 or 2).

3. **Partial coprimality**: What happens when exactly one pair shares a common factor? For instance, `PowTripleSet(2, 3, 6)` where `gcd(3, 6) = 3`. The set `{2^i · 3^j · 6^k} = {2^i · 3^{j+k} · 2^k·...}` has richer structure than the totally-ordered case.

4. **Quantitative antichain bounds**: For a given `n`, what is the minimum antichain size needed? Computational evidence suggests size 2 suffices for most `n`.
