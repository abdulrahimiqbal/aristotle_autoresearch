# Summary of changes
# Erdős Problem 123: d-Completeness of {a^k b^l c^m}

## What Was Accomplished

### Proved Lemmas (9 lemmas, all verified with clean axioms)
The following structural infrastructure was built and fully proved in `Main.lean`:

1. **Membership lemmas**: `one_mem_PowTripleSet`, `pow_mem_PowTripleSet_a/b/c`, `mul_mem_PowTripleSet` — establishing that 1, pure powers, and products are in the set.

2. **`dvd_iff_exponents_le`** — The key structural workhorse: for pairwise coprime a, b, c > 1, divisibility `a^i₁·b^j₁·c^k₁ ∣ a^i₂·b^j₂·c^k₂` holds if and only if `i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂`. This reduces all divisibility questions to arithmetic on exponent triples.

3. **`same_level_antichain`** — Elements at the same level (i+j+k = L) with distinct exponent triples are pairwise incomparable in divisibility.

4. **`staircase_antichain`** — Elements forming a "staircase" pattern (first coordinates increasing, second decreasing) are pairwise incomparable.

5. **`bc_incomparable_with_power_a`** — BC-plane elements (with j+k ≥ 1) are incomparable with pure a-powers (I ≥ 1).

6. **`IsDComplete.mono`** — d-completeness is monotone under set inclusion.

7. **`isDivisionAntichain_singleton`** — Singletons are trivially antichains.

### Remaining Sorry (1)
The main theorem `erdos_123_d_complete_sequences` — that PowTripleSet(a,b,c) is d-complete for all pairwise coprime a, b, c > 1 — remains unproved. This is a research-level result related to Erdős Problem 123.

## Key Discovery: Two-Generator d-Completeness is FALSE

A critical finding during the analysis: **the natural two-generator reduction fails**. The set `{m^i · n^j : i,j ≥ 0}` is NOT d-complete in general, even for coprime m, n > 1. 

**Counterexample**: For m=4, n=3, antichain sums can only achieve residues {0, 1, 3} mod 4. Residue 2 mod 4 is never achievable, because in any antichain, at most one element can be a pure power of 3 (all pure 3-powers form a chain), and elements with positive 4-exponent contribute 0 mod 4.

This means the initial proof strategy (reduce to two generators via PowPairSet(a·b, c) ⊆ PowTripleSet(a,b,c)) is invalid — the subset is not d-complete.

## Why Three Generators Succeed

Three generators overcome the residue obstruction because antichains in the (j,k)-plane (ℕ²) can have **multiple elements** (unlike the 1D case). For example, in PowTripleSet(4,3,5), the elements 9 = 3² and 5 are incomparable (exponents (0,2,0) vs (0,0,1)), and their sum 14 ≡ 2 (mod 4) — achieving the previously forbidden residue.

## Assessment: Easier or Harder?

The d-completeness reformulation is **structurally cleaner** (separating exponent-space properties from density arguments) but **mathematically equivalent in difficulty**. The core challenge — showing antichain sums eventually cover all integers — remains a deep result requiring:
1. Residue coverage via 2D antichains in the (j,k)-plane
2. Subset sum completeness arguments for level sets
3. Range overlap between consecutive levels

## Transferable Special Cases

See `ANALYSIS.md` for the full analysis. Key transferable results:
- The `dvd_iff_exponents_le` characterization transfers universally
- The `same_level_antichain` property works for all coprime triples
- The two-generator failure analysis identifies which subsets are NOT d-complete
- The 2D antichain residue coverage insight is the critical mechanism enabling three-generator d-completeness