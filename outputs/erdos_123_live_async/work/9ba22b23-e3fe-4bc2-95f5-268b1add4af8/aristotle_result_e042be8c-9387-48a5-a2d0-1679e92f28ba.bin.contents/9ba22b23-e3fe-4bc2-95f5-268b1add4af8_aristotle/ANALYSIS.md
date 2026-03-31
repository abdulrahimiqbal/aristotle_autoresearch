# Erdős Problem 123: d-Completeness Analysis

## Reformulation Assessment

**Question**: Is the reformulation as "the set {a^k b^l c^m : k, l, m ≥ 0} is d-complete" easier or harder to prove?

**Answer**: The reformulation is **structurally cleaner but mathematically equivalent in difficulty**. The key advantage of this formulation is that it cleanly separates the problem into:
1. Structural properties of the exponent space (ℕ³ under componentwise ≤)
2. The subset sum / covering problem for antichain elements
3. The density properties of smooth numbers

However, the core mathematical difficulty — showing that antichain sums eventually cover all integers — remains equally hard.

## Key Discovery: Two-Generator d-Completeness is FALSE

A critical finding during this analysis: **the two-generator analogue `PowPairSet(m, n) = {m^i · n^j}` is NOT d-complete in general**, even for coprime m, n > 1.

### Counterexample
For `PowPairSet(4, 3)`:
- In any divisibility antichain from this set, at most ONE element can have `i = 0` (a pure power of 3), since all pure 3-powers form a chain under divisibility.
- Elements with `i ≥ 1` are divisible by 4, contributing 0 mod 4.
- The single `i = 0` element contributes `3^j mod 4 ∈ {1, 3}`.
- Therefore, antichain sums can only achieve residues **{0, 1, 3} mod 4**.
- **Residue 2 mod 4 is never achievable**, so integers ≡ 2 (mod 4) are never representable.

This obstruction applies to `PowPairSet(m, n)` whenever the multiplicative subgroup ⟨n mod m⟩ is a proper subgroup of (ℤ/mℤ)*.

### Why Three Generators Overcome This
With three pairwise coprime generators, the "BC-plane" elements {b^j · c^k : j, k ≥ 0} live in ℕ², where antichains can have **multiple elements**. For example:
- In `PowTripleSet(4, 3, 5)`: elements (0,2,0) = 9 and (0,0,1) = 5 are incomparable.
- Sum 9 + 5 = 14 ≡ 2 (mod 4), achieving the previously forbidden residue.

The structural reason: antichains in ℕ² grow **quadratically** per level (size ∝ L² elements at level L), while antichains in ℕ¹ (two-generator case) grow only **linearly**. This quadratic growth provides enough flexibility to cover all residue classes.

## Proved Lemmas (Verified, No Sorries)

1. **`one_mem_PowTripleSet`**: 1 ∈ PowTripleSet a b c
2. **`pow_mem_PowTripleSet_a/b/c`**: Pure powers of each generator are in the set
3. **`mul_mem_PowTripleSet`**: The set is closed under multiplication
4. **`dvd_iff_exponents_le`**: For pairwise coprime generators, divisibility ↔ componentwise ≤ on exponents
5. **`isDivisionAntichain_singleton`**: Singletons are trivially antichains
6. **`same_level_antichain`**: Elements at the same level (i+j+k = L) are pairwise incomparable
7. **`IsDComplete.mono`**: d-completeness is monotone under set inclusion
8. **`staircase_antichain`**: Staircase patterns (i increasing, j decreasing) give incomparable elements
9. **`bc_incomparable_with_power_a`**: BC-plane elements are incomparable with pure a-powers

## Remaining Sorry: Main Theorem

The main theorem `erdos_123_d_complete_sequences` remains unproved. The proof requires showing that for all sufficiently large N, an antichain subset of PowTripleSet sums to N.

### Proof Strategy (Not Yet Formalized)
1. **Residue Coverage**: For any modulus M and residue r, there exists a finite antichain A in the BC-plane with Σ A ≡ r (mod M). This uses the 2D antichain structure and additive generation of ℤ/Mℤ by the elements {b^j · c^k mod M}.

2. **Greedy Construction**: For large N:
   - Set I = ⌊log_a(N)⌋, so a^I ≤ N < a^{I+1}
   - Set R = N - a^I
   - Find an antichain A of BC-plane elements (all with i < I, j+k ≥ 1) summing to R
   - Then {a^I} ∪ A is the desired antichain

3. **Subset Sum Coverage**: Show that BC-plane antichains can achieve any target sum R in the required range. This requires a careful analysis combining:
   - Level-L antichains {b^j · c^{L-j} : 0 ≤ j ≤ L}
   - Cross-level staircase antichains
   - Density estimates for smooth numbers

## Discovery Question: Transferable Special Cases

**Question**: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?

### Answer

1. **The "same-level" antichain property transfers universally**: The lemma `same_level_antichain` — that elements with i+j+k = L are pairwise incomparable — holds for ALL triples (a,b,c) with pairwise coprimality. This is the most reusable structural result.

2. **The divisibility characterization `dvd_iff_exponents_le` is the key workhorse**: Once established, it reduces all divisibility questions to arithmetic on exponents, enabling clean proofs of antichain properties.

3. **Monotonicity (`IsDComplete.mono`) enables modular reductions**: If ANY d-complete subset can be identified within PowTripleSet, the full set inherits d-completeness. However, the natural two-generator reduction `PowPairSet(ab, c) ⊆ PowTripleSet(a,b,c)` **fails** because PowPairSet is not generally d-complete.

4. **The residue obstruction analysis transfers as a negative result**: The proof that two-generator sets can have residue obstructions (blocking d-completeness) is a reusable technique for identifying WHICH subsets are NOT d-complete. This narrows the search for valid proof paths.

5. **The three-generator residue coverage property is the critical special case**: The fact that 2D antichains in the (j,k) plane can achieve all residue classes mod a (while 1D antichains cannot) is the fundamental reason why three generators succeed. This insight should transfer to any proof attempt for the general case.

### Broader Implications
The reformulation reveals a **sharp phase transition**: d-completeness of {m₁^{e₁} · ... · mₖ^{eₖ}} depends critically on the dimension k of the exponent space:
- **k = 1** (single generator): Never d-complete (only powers of m are representable)
- **k = 2** (two generators): Fails in general due to residue obstructions
- **k ≥ 3** (three or more generators): Conjectured to always work for pairwise coprime generators > 1, with the 2D antichain structure providing the missing coverage
