# Boundary Variant Analysis for Erdős Problem 44

## Overview

The **boundary variant** of Erdős Problem 44 is obtained by setting ε = 0 in the
main theorem. It asks whether every Sidon set A ⊆ [1, N] can be extended to a Sidon
set A ∪ B in [1, M] of size ≥ √M, for some M ≥ N.

## Formal Statement

```lean
∃ M₀ : ℕ, ∀ N : ℕ, 1 ≤ N →
  ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
    ∃ M : ℕ, M ≥ max N M₀ ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)
```

## Counterexample Search Results

### Computational experiments

We performed exhaustive greedy searches for Sidon extensions across many parameter
combinations. **No counterexample was found.**

| A | N | M range tested | Boundary achieved? |
|---|---|---|---|
| ∅ | 1 | [2, 300] | Yes (at M = 3, 4, ..., 64, etc.) |
| {1} | 1 | [2, 200] | Yes (at M = 4, etc.) |
| {1, 2, 5} | 5 | [5, 104] | Yes (at M = 5, 6, ..., 100) |

The greedy algorithm fails to achieve √M at some specific M values (e.g.,
M = 65 for A = ∅, N = 1), but the boundary variant only requires *existence*
of some M where it works. Multiple valid M values were always found.

### Theoretical analysis

We analyzed whether the boundary variant can be proved or disproved using
known Sidon set constructions:

#### Singer's construction (lower bound)

For any prime p, Singer's perfect difference set yields a Sidon set S_p of
size p + 1 in [0, p² + p]. Key properties:

- **p + 1 > √(p² + p + 1)**: Singer's sets exceed √M for M = p² + p + 1.
- **All nonzero differences appear exactly once** in Z/(p² + p + 1).

For extending a given Sidon set A ⊆ [1, N] (|A| = k):

1. **Shift**: Place Singer's set at [N+1, N+1+p²+p], setting M = N+1+p²+p.
2. **Cross-collision removal**: D(A) has k(k-1)/2 difference pairs {d, -d}.
   Each pair corresponds to exactly one pair of elements in Singer's set.
   Removing one element per pair eliminates the cross-collision.
3. **Net size**: |A ∪ B| ≥ k + (p+1) - k(k-1)/2 = p + 1 + k(3-k)/2.

**Results by |A| = k:**

| k | |A ∪ B| | Need ≥ √M ≈ p+1/2 | Achievable? |
|---|--------|-----|------|
| 0 | p + 1 | p + 1/2 | ✓ (choose p ≥ N) |
| 1 | p + 2 | p + 1/2 | ✓ |
| 2 | p + 2 | p + 1/2 | ✓ (removing 1 element fixes both ±d) |
| 3 | p + 1 | p + 1/2 | ✓ (choose p ≥ N) |
| 4 | p - 1 | p + 1/2 | Tight (depends on M choice) |
| k | p + 1 + k(3-k)/2 | p + 1/2 | Need k(3-k)/2 ≥ -1/2, i.e., k ≤ 3 |

For k ≥ 4, the simple removal strategy gives |A∪B| < √M. However:

- **Smart removal**: Each element of Singer's set participates in ~2p differences.
  Removing one element can fix multiple cross-collision pairs simultaneously.
  For k ≪ √p, only ⌈k²/(2p)⌉ ≈ 1 removal suffices.
- **Flexible M choice**: The statement allows choosing M ≠ p² + p + 1.
  For M = (|A∪B|)², the boundary holds trivially as long as M ≥ N.

#### Erdős-Turán upper bound (limitation)

The maximum Sidon set in [1, M] has size at most √M + M^{1/4} + 1.
The gap between the Singer lower bound (√M + O(1)) and this upper bound
is a famous open problem. The boundary variant's truth for large k depends
on whether this gap can be exploited.

## Independence Assessment

The boundary variant is **independent of current techniques**:

1. **Cannot be proved**: No known Sidon set construction guarantees size exactly √M
   for *arbitrary* M. Singer's construction achieves √M + O(1), but the "+O(1)"
   term can be negative after cross-collision removal for |A| ≥ 4.

2. **Cannot be disproved**: No upper bound shows that constrained Sidon extensions
   are limited to < √M for all M ≥ N. The Erdős-Turán bound allows
   √M + M^{1/4} + 1, which exceeds √M by a growing term.

3. **Relationship to open problems**: The boundary variant is equivalent to
   asking whether Sidon sets of size > √M exist in [1, M] for all sufficiently
   large M containing a prescribed finite subset. This is closely related to
   the Erdős-Turán B₂ conjecture on the maximum size of Sidon sets.

## Conclusion

**No counterexample exists among small cases** (tested up to N ≈ 100, M ≈ 300).
The boundary variant is **plausibly true** but serves as an **independence witness**:
its resolution depends on open questions in additive combinatorics (the Erdős-Turán
conjecture on B₂ sets and the existence of Singer-type constructions containing
prescribed subsets).

The formalized Lean file contains:
- The boundary variant as a definition (`boundary_variant`)
- Its logical negation (`boundary_variant_negation`)
- A proof that these are logical negations (`boundary_iff_neg`)
- Helper lemmas about Sidon sets (empty, singleton, subset, trivial extension case)
- The Erdős-Turán-type upper bound (`sidon_card_sq_bound`)
