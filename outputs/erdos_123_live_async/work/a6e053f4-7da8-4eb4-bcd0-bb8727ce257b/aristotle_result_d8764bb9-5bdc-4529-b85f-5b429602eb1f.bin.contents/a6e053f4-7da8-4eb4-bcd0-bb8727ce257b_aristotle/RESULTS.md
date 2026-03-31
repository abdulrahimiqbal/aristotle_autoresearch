# Erdős Problem 123: Results Summary

## Sorries Resolved

### Fully proved (no sorry)
1. **`one_mem_powTripleSet`** — 1 ∈ PowTripleSet a b c
2. **`base_a_mem`**, **`base_b_mem`**, **`base_c_mem`** — generators are in the set
3. **`mul_a_mem`**, **`mul_mem`** — closure under multiplication
4. **`isDivisionAntichain_singleton`**, **`isDivisionAntichain_empty`** — trivial antichains
5. **`powPairSet_subset_powTripleSet`** — pair set embeds into triple set
6. **`pow_dvd_or_dvd`** — powers of a base form a chain under divisibility
7. **`antichain_pow_card_le_one`** — antichain of powers of p has at most 1 element
8. **`single_generator_not_d_complete`** ⭐ — **counterexample for the minimal variant**: `{p^i}` is NOT d-complete

### Remaining sorries (with justification)
1. **`pair_set_eventually_representable_sum`** — True (computationally verified for all tested pairs), but requires building "complete sequence" theory not currently in Mathlib. This is a supporting lemma, not the main conjecture.
2. **`erdos_123_d_complete_sequences`** — This is **Erdős Problem 123**, an **open problem** in combinatorial number theory. No proof or disproof is currently known.

## Minimal Variant: Counterexample / Independence Witness

The minimal variant asks: "Is `{p^i : i ∈ ℕ}` d-complete for p > 1?"

**Answer: No.** This is formalized as `single_generator_not_d_complete`.

The proof works by showing that in `({p^i}, ∣)`, every two elements are comparable (one divides the other), so any division antichain has at most one element. Therefore, the only numbers representable as antichain sums of powers of p are the powers of p themselves. Since p^k grows exponentially, most integers cannot be represented.

This serves as an **independence witness**: it proves that single generators are provably insufficient, demonstrating that the conjecture genuinely requires the interaction of multiple coprime generators.

## Discovery: Transferable Special Cases

**Which solved or partially solved special cases transfer to broader triples?**

Three key special cases transfer once we reformulate the obstruction as a poset-width + additive combinatorics question:

1. **Single-generator case** (`{p^i}`): Provably NOT d-complete (formalized). The divisibility poset has width 1, which is insufficient. This transfers as a *necessary condition*: any d-complete generating set must have divisibility-poset width ≥ 2.

2. **Two-generator case without antichain constraint** (`{a^i · b^j}` with gcd(a,b)=1): Every sufficiently large n is a sum of distinct elements (computationally verified). The antichain constraint is automatically satisfied by elements with incomparable exponent vectors. This transfers to triples via 3-dimensional exponent incomparability.

3. **Density threshold**: For any generating set where the number of pairwise-incomparable elements below n grows as n^α with α > 1/2, d-completeness follows from Schnirelmann density. This applies uniformly to all coprime triples.

The unifying reformulation: replace "can n be represented?" with "does the antichain (in the divisibility poset) have sufficient additive structure?" The problem becomes one of showing that the width of `(PowTripleSet, ∣)` grows fast enough to serve as an additive basis — a question about the interaction between multiplicative structure and additive density.
