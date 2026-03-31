# Discovery Analysis: d-Completeness Boundary Cases

## Question
Which d-completeness boundary cases fail because interval-style coverage cannot
be upgraded to a divisibility antichain, and what is the sharpest witness?

## Answer

### The Sharpest Witness: (2, 4, 8)

The sharpest witness for the failure of the interval-to-antichain upgrade is
**(a, b, c) = (2, 4, 8)**. This triple satisfies:

1. **All generators > 1**: 2, 4, 8 are all > 1.
2. **NOT pairwise coprime**: gcd(2,4) = 2, gcd(2,8) = 2, gcd(4,8) = 4.
3. **Interval coverage succeeds**: PowTripleSet(2, 4, 8) = {2^n : n ∈ ℕ},
   and every positive integer is a sum of distinct powers of 2 (binary
   representation).
4. **Antichain upgrade fails catastrophically**: In {2^n : n ∈ ℕ}, every pair
   (2^a, 2^b) with a < b satisfies 2^a | 2^b. Thus any divisibility antichain
   has at most one element, so antichain sums are exactly {0} ∪ {2^n : n ∈ ℕ}.
   Most positive integers (e.g., 3, 5, 6, 7, ...) have no antichain-sum
   representation.

This is **formally verified** in `AristotleWorkspace/Counterexample.lean`:
- `powTripleSet_248_eq_pow2`: PowTripleSet 2 4 8 = {2^n}
- `antichain_pow2_card_le_one`: antichains in {2^n} have card ≤ 1
- `interval_coverage_pow2`: every positive integer has a sum-of-distinct-powers-of-2 representation
- `negated_weakening_counterexample`: PowTripleSet 2 4 8 is NOT d-complete

### Why (2, 4, 8) Is the Sharpest

This witness is "sharpest" because:

- **Maximal interval coverage**: Every positive integer is representable as a
  sum of distinct elements (the strongest possible form of interval coverage).
- **Minimal antichain coverage**: The antichain constraint collapses to
  singletons, yielding the starkest possible gap between interval coverage
  and antichain coverage.
- **The failure is structural**: It's not about "almost" being able to form
  antichains — no pair from the set is ever incomparable in divisibility.

### Boundary Case Classification

The boundary cases where interval coverage fails to upgrade to antichain
coverage fall into three categories:

#### Category 1: All generators share a common prime (total collapse)
**Examples**: (2, 4, 8), (3, 9, 27), (p, p², p³) for any prime p.

PowTripleSet = {p^n : n ∈ ℕ}, a totally ordered set under divisibility.
Antichains have size ≤ 1. Interval coverage holds (by p-ary representation
for appropriate primes) but antichain sums are trivially limited.

**This is the sharpest failure mode.**

#### Category 2: Two generators share a prime, one is coprime (partial collapse)
**Examples**: (2, 4, 3), (2, 6, 5), (3, 9, 5).

PowTripleSet is richer — e.g., for (2, 4, 3), we get {2^m · 3^n : m, n ∈ ℕ}
(3-smooth numbers). Antichains can be larger (e.g., {4, 3} is an antichain
since gcd(4,3) = 1). Interval coverage likely holds, and the antichain
upgrade may partially succeed. These are **borderline cases** whose
d-completeness status depends on the specific generators.

For (2, 3, 6): PowTripleSet = {2^m · 3^n : m, n ∈ ℕ}. Antichains exist
(e.g., {2, 3}, {4, 9}, {8, 27}). Whether ALL sufficiently large integers
have antichain-sum representations is a non-trivial question — this is
the "two-generator" version of the problem, related to Folkman's results.

#### Category 3: Pairwise coprime generators (the theorem's hypothesis)
**Examples**: (2, 3, 5), (2, 3, 7), (3, 5, 7).

Erdős Problem 123 conjectures (and partial results confirm) that these are
all d-complete. The three-axis antichain structure provides enough degrees
of freedom to cover all sufficiently large integers.

### The Coprimality Boundary

The critical dividing line is **pairwise coprimality**:
- With pairwise coprimality, the exponent lattice ℕ³ has rich antichain
  structure (any two elements from different axes are incomparable), and
  this richness enables d-completeness.
- Without pairwise coprimality, the exponent lattice partially or fully
  collapses, merging axes and reducing antichain freedom. The (2, 4, 8)
  witness shows this collapse is total when all generators share a prime.

### Connection to the Negated Weakening

The "negated weakening" — dropping PairwiseCoprime3 from the hypothesis of
Erdős Problem 123 — is REFUTED by the (2, 4, 8) counterexample. This shows
the coprimality hypothesis is **necessary** for d-completeness, not just
a technical convenience.

Formally: ∃ a b c, 1 < a ∧ 1 < b ∧ 1 < c ∧ ¬PairwiseCoprime3 a b c ∧
¬IsDComplete (PowTripleSet a b c). Witness: (2, 4, 8).
