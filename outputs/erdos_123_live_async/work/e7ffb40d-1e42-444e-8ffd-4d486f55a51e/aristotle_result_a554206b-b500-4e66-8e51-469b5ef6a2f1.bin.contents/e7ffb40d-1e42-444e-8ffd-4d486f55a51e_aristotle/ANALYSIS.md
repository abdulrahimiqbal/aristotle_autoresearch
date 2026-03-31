# Erdős Problem 123 — Perturbation Analysis

## Perturbation Applied

The antichain condition (`IsDivisionAntichain`) has been **removed** from the
definition of `IsDComplete`. The original requirement was:

> Every sufficiently large integer admits a representation as a sum of distinct
> elements from PowTripleSet(a, b, c), **where no chosen summand divides another**.

After perturbation:

> Every sufficiently large integer admits a representation as a sum of distinct
> elements from PowTripleSet(a, b, c).

This is a strict weakening — any d-complete set in the original sense is also
d-complete in the perturbed sense (formalized as `isDComplete_of_antichain`).

---

## Does the proof close?

**Partially.** The proof closes for all triples (a, b, c) where at least one
element equals 2. It does **not** close for triples where all three elements
are ≥ 3 (e.g., (3, 5, 7), (3, 4, 5), (4, 9, 25)).

### What is proved (sorry-free)

| Lemma / Theorem | Status |
|---|---|
| `isDComplete_of_antichain` | ✅ Proved |
| `isDComplete_mono` | ✅ Proved |
| `one_mem_powTripleSet` | ✅ Proved |
| `pow_a_mem`, `pow_b_mem`, `pow_c_mem` | ✅ Proved |
| `mem_powTripleSet_iff` | ✅ Proved |
| `mul_mem_powTripleSet` | ✅ Proved |
| `powTripleSet_swap12`, `powTripleSet_swap23` | ✅ Proved |
| `brown_completeness_criterion` | ✅ Proved |
| `powTripleSet_2bc_dComplete` | ✅ Proved |
| `pow_ne_pow_of_coprime` | ✅ Proved |
| `irrational_log_ratio` | ✅ Proved |
| `erdos_123_d_complete_sequences` (when min(a,b,c) = 2) | ✅ Proved |

### What remains (sorry)

| Lemma | Blocker |
|---|---|
| `exists_close_pair` | Diophantine approximation → integer conversion |
| `powPair_eventually_dense` | Depends on `exists_close_pair` |
| `erdos_123_d_complete_sequences` (all ≥ 3 case) | Depends on `powPair_eventually_dense` |

---

## The blocker: Density of smooth numbers

The **single mathematical blocker** is proving that for coprime a, b ≥ 2, the
multiplicative semigroup {a^i · b^j : i, j ∈ ℕ} is *eventually dense on a
multiplicative scale*: for all M sufficiently large, there exists an element
in (M, 2M].

### Why this is hard to formalize

The standard proof proceeds via:

1. **Irrationality**: log(a)/log(b) is irrational for coprime a, b > 1, a ≠ b.
   *(Proved as `irrational_log_ratio`)*

2. **Dirichlet's approximation theorem**: For irrational ξ and any N, there
   exist integers k, j with 0 < k ≤ N and |kξ - j| ≤ 1/(N+1).
   *(Available in Mathlib as `Real.exists_int_int_abs_mul_sub_le`)*

3. **Close pair existence**: From (1) and (2), deduce that there exist
   positive p, q with b^q < a^p ≤ 2·b^q.
   *(Stated as `exists_close_pair`, NOT proved — the translation between
   real approximation and integer bounds creates coercion challenges)*

4. **Density from close pair**: Using the multiplicative shift (p, -q),
   show that for large M, (M, 2M] contains an element.
   *(Stated as `powPair_eventually_dense`, depends on step 3)*

5. **Brown's criterion**: Conclude d-completeness.
   *(Proved as `brown_completeness_criterion`)*

Step 3 is the critical formalization gap. It requires translating a real-valued
approximation |k · log(a)/log(b) - j| < ε into the integer inequality
b^q < a^p ≤ 2 · b^q, handling:
- Conversion between ℝ and ℕ exponentials
- Sign analysis (the approximation could be from above or below)
- The case a = b (excluded by coprimality)

---

## Discovery: Which special cases transfer?

### Fully transferable cases

1. **Any triple with 2 as a generator**: (2, b, c) for arbitrary b, c > 1,
   pairwise coprime. Binary representation provides d-completeness with no
   coprimality or structural requirements beyond 2 being present.
   *This covers a large family including (2, 3, 5), (2, 3, 7), (2, 5, 9), etc.*

2. **Permutations**: PowTripleSet is symmetric in all three arguments
   (proved as `powTripleSet_swap12`, `powTripleSet_swap23`), so the (2, b, c)
   result immediately transfers to (b, 2, c) and (b, c, 2).

### Partially transferable cases (via the density route)

Once `exists_close_pair` and `powPair_eventually_dense` are established:

3. **All odd triples (a, b, c) with a, b, c ≥ 3**: The density argument
   applies uniformly. The proof structure (Brown's criterion + density) is
   identical for all such triples — no case-specific analysis is needed.

4. **Triples with even elements ≥ 4**: e.g., (4, 3, 5), (6, 5, 7). These
   are also covered by the same density argument. The coprimality constraint
   is the only structural requirement.

### The obstruction, reformulated

The **obstruction** to closing the proof is not mathematical (the theorem is
true) but *formalization-theoretic*: the translation layer between Dirichlet's
approximation theorem (stated over ℝ) and the integer-valued close pair
lemma requires navigating Lean's coercion system across ℕ, ℤ, and ℝ while
maintaining positivity constraints and handling floor/ceiling operations.

**Key insight**: The obstruction is *uniform across all coprime triples with
min ≥ 3*. Once `exists_close_pair` is proved for general coprime a, b ≥ 2,
ALL remaining cases close simultaneously via `powPair_eventually_dense` and
Brown's criterion. There is no triple-specific obstruction — the difficulty
is entirely in the base infrastructure lemma.

### Recommendation for future work

The most impactful single contribution would be formalizing `exists_close_pair`
in Mathlib as a standalone result:

```
theorem exists_close_pair {a b : ℕ} (ha : 1 < a) (hb : 1 < b)
    (hab : Nat.Coprime a b) :
    ∃ p q : ℕ, 0 < p ∧ b ^ q < a ^ p ∧ a ^ p ≤ 2 * b ^ q
```

This would unlock not just Erdős 123 but any result depending on the
multiplicative density of coprime power products.
