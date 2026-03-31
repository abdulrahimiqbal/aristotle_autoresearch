# Summary of changes
## Summary

### Reformulation via Transfer Decomposition

The original Erdős Problem 123 conjecture about d-completeness of multiplicative triples `{a^i · b^j · c^k}` has been reformulated using the transferable artifact "special-case covering lemmas can often be transferred by isolating the divisibility obstruction" from additive number theory.

The reformulation in `Main.lean` decomposes d-completeness into two independent components:

1. **Additive covering** (`HasAdditiveCovering`): Every sufficiently large integer is a sum of distinct elements from the power triple set.
2. **Antichain upgrade** (`HasAntichainUpgrade`): Any additive representation can be refined to a divisibility-antichain representation.

A **composition theorem** (`dComplete_of_covering_and_upgrade`) proves that these two properties together imply d-completeness.

### Proved Theorems (all sorry-free)

- **`divisibility_iff_coordinate_domination`**: In a pairwise-coprime triple, divisibility equals coordinate-wise domination. This is the key structural lemma enabling the antichain upgrade.
- **`dComplete_of_covering_and_upgrade`**: The composition theorem connecting covering + upgrade → d-completeness.
- **`covering_with_generator_2`**: When one generator is 2, binary representation gives additive covering trivially.
- **`powTripleSet_100_101_103_small_elements`**: Characterizes elements ≤ 305 in the (100,101,103) power set, demonstrating epoch-gap structure.
- **`not_representable_306`**: 306 is not representable from PowTripleSet(100,101,103), witnessing epoch-gap obstructions.
- **`pairwiseCoprime_100_101_103`**: Verifies (100,101,103) is pairwise coprime.
- **Boundary witnesses**: `boundary_witness_not_coprime`, `boundary_witness_div_obstruction`, `boundary_witness_not_coprime_248`, `powTripleSet_248_eq_pow2`, `three_not_pow2` — all proving structural properties of the boundary cases.
- **Basic structural lemmas**: `one_mem_powTripleSet`, `generator_mem_powTripleSet_a/b/c`, `mul_mem_powTripleSet`, `pos_of_mem_powTripleSet`, `pow2_mem_powTripleSet`.

### Remaining Sorry (1 total)

- **`erdos_123_d_complete_sequences`**: The main Erdős Problem 123 conjecture. This is an **open problem** in combinatorial number theory. The file provides the complete decomposition infrastructure; only the core mathematical content remains unproven.

### Discovery Question Answer

**Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?**

Three distinct failure mechanisms were identified and formally witnessed:

1. **Divisibility antichain failure** (non-coprime generators): `(2, 4, 3)` — `gcd(2,4) = 2` creates unavoidable divisibility chains. Formally proved: `boundary_witness_not_coprime` and `boundary_witness_div_obstruction`.

2. **Total order collapse** (common prime base): `(2, 4, 8)` — all elements are powers of 2, making the divisibility order total. Only singletons are antichains, so d-completeness fails for non-powers-of-2 like 3. Formally proved: `powTripleSet_248_eq_pow2` and `three_not_pow2`.

3. **Epoch gap obstruction** (sparse generators): `(100, 101, 103)` — elements cluster into "epochs" separated by large gaps. Formal witness: `not_representable_306` (dead zone [306, 9999]). Computational analysis shows dead zones persist through at least epoch 5, but the ratio S_k/100^(k+1) grows, suggesting they eventually vanish — consistent with the conjecture being true with an astronomically large threshold.

The **sharpest witness** is `(2, 4, 8)`: it isolates the divisibility obstruction most cleanly, showing that without coprimality, the divisibility order can become total, collapsing all antichains to singletons.