# Erdős Problem 123: D-Completeness Analysis

## Summary

This project formalizes the infrastructure for **Erdős Problem 123** — the conjecture
that for pairwise coprime integers a, b, c > 1, the multiplicative semigroup
{a^i · b^j · c^k : i, j, k ≥ 0} is **d-complete** (every sufficiently large integer
can be written as an antichain sum from this set).

## What was proved

### Core structural lemmas (all formally verified):

1. **`powTriple_not_dvd_of_incomparable`** — The fundamental reusable covering lemma:
   divisibility in PowTripleSet is equivalent to componentwise ≤ on exponent triples.
   This reduces antichain checking to lattice-theoretic comparisons in ℕ³.

2. **`antichain_same_level`** — Elements at the same "level" (i+j+k = L) always form
   a divisibility antichain. This provides (L+1)(L+2)/2 antichain elements at level L.

3. **`scale_antichain_rep`** — If n has an antichain representation, then a·n also does
   (multiply each antichain element by a). This shows the representable set (RepSet)
   is closed under multiplication by generators.

4. **`frobenius_two_coprime`** — For coprime a, b > 1, all sufficiently large integers
   are non-negative combinations of a and b (Sylvester–Frobenius theorem).

5. **`pair_antichain`** — For coprime a, b > 1, {a, b} is always an antichain.

6. **`sum_pair_representable`** — a + b is always representable from PowTripleSet.

7. **`pair_ab_c_antichain`** — {a·b, c} is always an antichain.

8. **`sum_ab_c_representable`** — a·b + c is always representable.

9. **`gcd_pairwise_sums_dvd_two`** — gcd(a+b, gcd(a+c, b+c)) divides 2.

### Adversarial witnesses (formally verified):

1. **`adversarial_coprime_sums_not_coprime`** — Refutes the hypothesis that pairwise
   sums a+b, a+c are always coprime. Counterexample: (a,b,c) = (3,5,7) gives
   gcd(8,10) = 2.

2. **`adversarial_even_sums_not_coprime`** — Refutes the "even element fixes the
   blocker" hypothesis. Counterexample: (a,b,c) = (2,3,13) gives gcd(5,15) = 5.

## What remains (the main theorem)

The theorem `erdos_123_d_complete_sequences` remains as `sorry`. This is a deep
result in additive number theory. The gap is in the **density/coverage argument**:
showing that the proven structural lemmas combine to cover all large integers.

## Discovery: Reusable Covering/Divisibility-Extraction Lemmas

The following lemmas recur across **all** parameter triples (a,b,c) and are strong
enough to promote to a general theory:

### Tier 1: Universal structural lemmas

- **Exponent-vector divisibility criterion** (`powTriple_not_dvd_of_incomparable`):
  The most fundamental. Converts divisibility in PowTripleSet to componentwise ≤ in ℕ³.
  Works for any pairwise coprime triple.

- **Level-based antichains** (`antichain_same_level`):
  Same-level elements form antichains automatically. Universal across all triples.

### Tier 2: Composition/scaling lemmas

- **Multiplicative scaling** (`scale_antichain_rep`):
  RepSet · PowTripleSet ⊆ RepSet. Enables "divide and conquer" proof strategies.

### Tier 3: Seed lemmas

- **Coprime pair antichains** (`pair_antichain`, `pair_ab_c_antichain`):
  Generate initial representable values (a+b, ab+c, etc.) for all triples.

- **Frobenius coverage** (`frobenius_two_coprime`):
  Provides the eventual-surjectivity backbone for any coprime pair.

### The blocker pattern '?'

The "blocker" is the **parity obstruction**: gcd(a+b, a+c, b+c) can be 2
(when all three bases are odd). This prevents naive two-generator Frobenius arguments.
The adversarial witnesses show this blocker is real and cannot be eliminated by
simple conditions (even/odd classification).

The resolution would require showing that:
- RepSet contains both even and odd numbers (from antichains of different sizes), AND
- The multiplicative closure under PowTripleSet combined with the parity structure
  eventually covers all integers.

This is the precise gap between the proved infrastructure and the full theorem.
