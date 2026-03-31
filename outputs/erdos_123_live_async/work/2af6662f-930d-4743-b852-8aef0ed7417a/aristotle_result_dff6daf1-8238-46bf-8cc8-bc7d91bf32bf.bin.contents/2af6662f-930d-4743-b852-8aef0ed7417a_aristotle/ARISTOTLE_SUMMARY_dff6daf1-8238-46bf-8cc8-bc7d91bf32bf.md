# Summary of changes
# Erdős Problem 123 — Reformulation and Structural Results

## What was done

The file `Main.lean` has been restructured around an extremal/boundary-case reformulation of Erdős Problem 123. All **provable** sorries have been filled in (11 theorems proved); the single remaining `sorry` is the main conjecture itself, which is a **genuinely open problem** in additive combinatorics.

## Proved results (no sorry)

1. **Membership lemmas**: `one_mem_powTripleSet`, `base_a_mem`, `base_b_mem`, `base_c_mem` — the identity and generators belong to PowTripleSet.
2. **Closure lemmas**: `mul_a_mem`, `mul_b_mem`, `mul_c_mem`, `mul_mem` — PowTripleSet is closed under multiplication by generators and by its own elements.
3. **Exponent uniqueness** (`exponent_unique`): For pairwise coprime bases > 1, the triple (i, j, k) in a^i·b^j·c^k is uniquely determined.
4. **Divisibility ⟺ componentwise ≤** (`div_iff_exponent_le`): The key structural theorem — for coprime bases, a^i₁·b^j₁·c^k₁ divides a^i₂·b^j₂·c^k₂ if and only if i₁≤i₂, j₁≤j₂, k₁≤k₂. This reduces the d-completeness problem to a combinatorial question about antichains in (ℕ³, ≤).
5. **Monotonicity** (`powTripleSet_monotone`): Elementwise comparison of PowTripleSets.
6. **d-completeness transfer** (`isDComplete_superset`, `isDComplete_mono`): d-completeness is monotone under set inclusion.
7. **Negative result** (`not_isDComplete_single_gen`): Single-generator sets {p^i} are provably NOT d-complete — the set is totally ordered under divisibility, so antichains have at most one element.

## The remaining open conjecture

`erdos_123_d_complete_sequences` — the full Erdős Problem 123 — remains `sorry`'d. This states that for any pairwise coprime a, b, c > 1, the set {a^i·b^j·c^k} is d-complete. This is a well-known open problem in number theory.

## Reformulation and discovery answer

**Extremal case**: (a, b, c) = (2, 3, 5) is the boundary — smallest pairwise coprime triple, densest PowTripleSet, and "easiest" case for d-completeness.

**Which special cases transfer?**
- The single-generator case {p^i} is proved NOT d-complete (totally ordered ⟹ antichains trivial). This shows ≥2 independent generators are necessary.
- Direct set-inclusion transfer between different triples generally fails: PowTripleSet(2,3,5) and PowTripleSet(7,11,13) are essentially disjoint sets.
- What DOES transfer is the **proof technique**: `div_iff_exponent_le` shows that ALL pairwise coprime triples share the same poset structure (ℕ³ with product order). Any proof that works through the poset-antichain structure plus density bounds automatically applies to all triples. The obstruction is uniform across the parameter space.