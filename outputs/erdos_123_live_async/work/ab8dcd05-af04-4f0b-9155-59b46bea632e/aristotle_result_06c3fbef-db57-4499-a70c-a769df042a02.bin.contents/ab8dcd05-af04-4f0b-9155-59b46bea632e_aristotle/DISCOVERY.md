# Erdős Problem 123 — Discovery Analysis

## Negated Weakening: Counterexample

**Proved** (`negated_weakening_counterexample`): Dropping pairwise coprimality invalidates d-completeness.

The triple `(2, 4, 8)` demonstrates this: since `2 | 4` and `4 | 8`, all elements of
`PowTripleSet 2 4 8 = {2^n : n ≥ 0}` form a single chain under divisibility. Any division
antichain from this set has at most one element, so the only achievable sums are individual
powers of 2. In particular, `3` is never representable, and d-completeness fails.

This is an **independence witness** for the coprimality hypothesis: removing it changes the
theorem from (conjecturally) true to provably false.

## Discovery: Which Special Cases Transfer?

The central question is: once we solve d-completeness for a specific triple `(a₀, b₀, c₀)`,
which other triples inherit the result?

### 1. Monotonicity Transfer (`dComplete_mono`)

If `PowTripleSet(a₀, b₀, c₀) ⊆ PowTripleSet(a, b, c)`, then d-completeness of the smaller
set implies d-completeness of the larger. This is proved as `dComplete_mono`.

**Consequence**: Any triple whose PowTripleSet contains a known d-complete set inherits the
property. For instance, adding a fourth generator can only help.

### 2. Shared-Factor Obstruction (`shared_factor_obstruction`)

If `d ≥ 2` divides all three generators, then every antichain sum (of elements ≠ 1) is
divisible by `d`. This proves that **non-coprime triples can never be d-complete** when the
shared factor prevents coverage of all residue classes.

**Transfer**: The `(2, 4, 8)` counterexample generalizes to any triple `(p^a, p^b, p^c)` where
`p` is prime — the "single-chain obstruction." More broadly, any triple where all generators
share a prime factor fails by the shared-factor obstruction.

### 3. Cross-Divisibility Structure (`coprime_cross_not_dvd`)

For pairwise coprime `a, b, c > 1`, the elements `a · c^k` and `b · c^l` are **never** in a
divisibility relation (proved as `coprime_cross_not_dvd`). This gives a uniform construction
of two-element antichains `{a · c^k, b · c^l}` across ALL pairwise coprime triples.

**Transfer**: This structural property is identical for every pairwise coprime triple, meaning
proof techniques based on two-element antichains transfer uniformly. The sums `a·c^k + b·c^l`
provide a base layer of representable integers that any proof can build on.

### 4. Proof Technique Transfer (Conjectured)

The full d-completeness proof for any specific triple (say `(2, 3, 5)`) would use:
- The antichain structure of ℕ³ under componentwise order
- Additive coverage via CRT and Frobenius-type arguments
- The exponential growth of elements ensuring large antichains

These ingredients depend only on pairwise coprimality, not on the specific values.
Therefore, **any complete proof for one triple would transfer to all triples** via the
same argument structure — the specific values `a, b, c` enter only through constants
(Frobenius number, multiplicative orders, etc.) that exist for any coprime triple.

### 5. The Key Obstruction, Reformulated

The obstruction to d-completeness can be reformulated as:

> The divisibility poset of PowTripleSet must have **width** (maximum antichain size)
> growing without bound, AND the **subset sums of antichains** must be dense enough
> to eventually cover all integers.

- **Width condition**: For pairwise coprime generators, the poset is isomorphic to ℕ³
  under componentwise order, which has antichains of every finite size. ✓
- **Density condition**: This is the hard part — it requires showing that the exponentially
  growing elements of PowTripleSet can be combined (via antichains) to hit every large integer.

When generators share a factor, the poset collapses toward a chain (bounded width),
and the density condition fails immediately. This is the precise reformulation of why
pairwise coprimality is necessary and (conjecturally) sufficient.

## Summary of Proved Results

| Statement | Status |
|---|---|
| `negated_weakening_counterexample` | ✅ Proved |
| `powTripleSet_2_4_8_eq` | ✅ Proved |
| `antichain_pow2_card_le_one` | ✅ Proved |
| `antichain_sum_pow2_is_pow2` | ✅ Proved |
| `three_ne_pow2` | ✅ Proved |
| `dComplete_mono` | ✅ Proved |
| `shared_factor_obstruction` | ✅ Proved |
| `coprime_cross_not_dvd` | ✅ Proved |
| `mem_powTripleSet_ac` | ✅ Proved |
| `mem_powTripleSet_bc` | ✅ Proved |
| `erdos_123_d_complete_sequences` | ❌ Open (Erdős Problem 123) |

The main theorem remains as the central open formalization target. Its proof requires
substantial additive combinatorics infrastructure (subset sum density results, complete
sequence theory) that is not currently available in Mathlib.
