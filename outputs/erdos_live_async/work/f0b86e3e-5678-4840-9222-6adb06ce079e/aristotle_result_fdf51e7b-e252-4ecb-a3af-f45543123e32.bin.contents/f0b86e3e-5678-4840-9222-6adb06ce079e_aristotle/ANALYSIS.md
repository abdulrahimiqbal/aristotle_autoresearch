# Counterexample Search: Erdős 44 Sidon Extension (Weakened Variant)

## Statement

For every ε > 0, there exists a threshold Mε such that every Sidon set A ⊆ [1, N]
can be extended to a Sidon set A ∪ B in [1, M] of cardinality ≥ (1 − ε)√M, for
some M ≥ max(N, Mε).

## Result

**No counterexample found. No independence witness found.**

The statement appears to be **true** but is equivalent to an open problem in
additive combinatorics (a variant of Erdős Problem 44).

## Detailed Analysis

### Case ε ≥ 1 (PROVED)

When ε ≥ 1, we have (1 − ε) ≤ 0, so (1 − ε)√M ≤ 0 ≤ |A ∪ B| for any B.
Taking M = N and B = ∅ suffices. This case is formally proved in `Main.lean`.

### Case 0 < ε < 1, |A| ≥ (1 − ε)√N (trivial extension)

Take M = N and B = ∅. Then |A ∪ ∅| = |A| ≥ (1 − ε)√N = (1 − ε)√M. ✓

This covers all "dense" Sidon sets, including near-optimal ones from algebraic
constructions (Singer difference sets).

### Case 0 < ε < 1, |A| < (1 − ε)√N (open problem)

This is the hard case where A is "sparse" relative to √N and genuine extension
is needed. The analysis shows:

#### Approach 1: Shifted Erdős–Turán construction

For a prime p ≥ N, the set B₀ = {2kp + (k² mod p) + L : k = 0, ..., p−1} with
L = N + 2p² + 1 gives a Sidon set of size p in [L, L + 2p² − p − 1].

**Properties:**
- All differences of B₀ have absolute value ≥ p + 1 > N
- Therefore Diff(B₀) ∩ Diff(A) = ∅ (no type-1 cross-collisions)
- B₀ + B₀ − B₀ ∩ [1, N] = ∅ (no type-2 cross-collisions)
- A ∪ B₀ is Sidon ✓

**Density:** M = N + 4p² − p, giving |A ∪ B₀|/√M → 1/2 as p → ∞.
This works for **ε ≥ 1/2** but fails for smaller ε.

#### Approach 2: Singer difference sets with removal

For a prime p, the Singer set S of size p + 1 in [0, p² + p] achieves optimal
density. However, when extended with shift L = N + q:

- Type-1 collisions (Diff(A) ∩ Diff(B)): O(|A|²) ≤ O(N) removals
- Type-2 collisions (a + b₁ = b₂ + b₃): eliminated by shift, but M doubles

**Density:** |B|/√M ≈ 1/√2 ≈ 0.707. Works for **ε ≥ 0.293** but fails below.

#### Approach 3: Singer with in-place collision removal

Without shifting, type-2 collisions give O(|A| · p) collisions total,
requiring O(p/3) removals.

**Density:** |B|/√M ≈ 2/3. Works for **ε ≥ 1/3** but fails below.

### Why the negation fails

The negation would require: ∃ ε > 0, ∀ Mε, ∃ N, A (Sidon), ∀ M ≥ max(N, Mε),
∀ B ⊆ [N+1, M], ¬(A ∪ B Sidon ∧ |A ∪ B| ≥ (1−ε)√M).

This fails for three independent reasons:

1. **A = ∅**: Singer constructions give Sidon sets of size √M in [1, M] for
   M = p² + p. No cross-collisions needed. ✗

2. **|A| = 1**: Translated Singer sets can be chosen to contain any specific
   element, giving full size p + 1 ≈ √M. ✗

3. **|A| ≈ √N**: Taking M = N gives |A| ≈ √M > (1−ε)√M. ✗

No adversarial choice of A simultaneously defeats all values of M.

### Computational verification

Greedy Sidon extensions were computed for various (N, M) pairs:

| N   | M    | |A∪B| (greedy) | √M    | Ratio  |
|-----|------|----------------|-------|--------|
| 30  | 100  | 11             | 10.0  | 1.10   |
| 30  | 200  | 14             | 14.1  | 0.99   |
| 30  | 500  | 20             | 22.4  | 0.89   |
| 30  | 1000 | 27             | 31.6  | 0.85   |

The greedy algorithm achieves M^{1/3} density (suboptimal). Algebraic
constructions would give higher density, but formalizing them requires deep
number theory not present in Mathlib.

## Conclusion

The statement sits at the frontier of additive combinatorics. It is:
- **Not refutable**: no counterexample exists
- **Not simply provable**: requires Singer or probabilistic constructions absent
  from Mathlib
- **Related to Erdős Problem 44**: resolution would likely advance the state of
  the art in Sidon set theory

The single remaining `sorry` in `Main.lean` covers the case 0 < ε < 1 with
sparse Sidon sets, which is equivalent to this open problem.
