# Erdős Problem 123: Counterexample Search Analysis

## Problem Statement

The theorem `erdos_123_d_complete_sequences` claims that for all pairwise coprime
integers `a, b, c > 1`, the multiplicative semigroup `{a^i · b^j · c^k : i,j,k ≥ 0}`
is d-complete: every sufficiently large integer can be written as a sum of distinct
elements forming a division antichain (no element divides another).

## Relationship to Known Mathematics

This is a generalization of **Erdős Problem 123**, which specifically asks whether
the set of 3-smooth numbers `{2^i · 3^j}` is d-complete. The problem remains open
as of 2024, even in the two-generator case. The three-generator universal formulation
in this file is strictly stronger.

## Counterexample Search Results

### Computational Evidence

1. **a=2, b=3, c=5 (5-smooth numbers):** All integers 1–100 are representable as
   antichain sums using elements ≤ 30. No gaps found.

2. **a=4, b=9, c=25 (perfect squares of 5-smooth numbers):** With elements up to
   ~1300 (20 elements), 1351 out of 2000 integers are NOT representable. Coverage
   improves with more elements but remains sparse at this scale.

3. **a=101, b=103, c=107 (close primes):** With only 14 elements up to 500, the
   vast majority of integers are not representable. Specific non-representability
   results were formally proved (see below).

### Formally Proved Non-Representability

We proved two specific non-representability results in Lean 4:

- **`no_antichain_sum_10203`**: n = 10203 = 101² + 2 has NO antichain sum
  representation from PowTripleSet(101, 103, 107).

- **`no_antichain_sum_1030303`**: n = 1030303 = 101³ + 2 has NO antichain sum
  representation from PowTripleSet(101, 103, 107).

### The Pattern: n = 101^m + 2

For (101, 103, 107), the numbers 101^m + 2 (for m ≥ 2) exhibit a systematic
non-representability pattern:

- **Including 101^m:** The remainder is 2, but the smallest division-antichain-compatible
  element is 103 > 2 (since 1 | 101^m and 101 | 101^m, making {1, 101^m} and
  {101, 101^m} NOT antichains).

- **Excluding 101^m:** For small m, the total sum of all other elements ≤ 101^m + 2
  falls far short of 101^m + 2.

This argument works for m = 2, 3, 4, ..., up to approximately m ≈ 80, after which
the total sum of lower-level elements exceeds 101^m (since 107 > 101).

### Why This Doesn't Constitute a Full Counterexample

The theorem claims eventual representability ("for all sufficiently large n"). Our
non-representability results only cover finitely many specific values. The theorem
could still be true with an astronomically large threshold (e.g., N₀ > 101^80 ≈ 10^160).

A full counterexample would require showing that for some fixed triple (a,b,c),
**infinitely many** integers are non-representable. This appears to require either:
- Proving the gaps never close (as hard as the original problem)
- Finding a modular or structural obstruction (none found)
- Proving independence from ZFC (unlikely for a concrete combinatorial statement)

## Auxiliary Results Proved

1. **`div_iff_exp_le`**: For pairwise coprime bases, divisibility between products
   a^i₁·b^j₁·c^k₁ and a^i₂·b^j₂·c^k₂ is equivalent to coordinate-wise ≤ on
   exponent vectors: i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂.

2. **`powTripleSet_101_103_107_le_10203`**: Complete enumeration of elements ≤ 10203.

3. **`powTripleSet_101_103_107_le_1030303`**: Complete enumeration of elements ≤ 1030303.

## Conclusion

The main theorem (`erdos_123_d_complete_sequences`) remains sorry'd as it is equivalent
to a generalization of a famous open problem. Our search found specific non-representable
numbers but no infinite family that would constitute a counterexample. The problem appears
genuinely open, requiring new techniques in additive combinatorics for resolution.
