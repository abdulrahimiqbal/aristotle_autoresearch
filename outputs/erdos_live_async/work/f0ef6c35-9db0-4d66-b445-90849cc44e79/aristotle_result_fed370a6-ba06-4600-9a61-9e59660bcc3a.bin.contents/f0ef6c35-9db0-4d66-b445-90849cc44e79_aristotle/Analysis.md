# Erdős Problem 44: Counterexample Search & Parameter Extreme Analysis

## Problem Statement

For all ε > 0, there exists Mε such that for all N ≥ 1 and all Sidon sets A ⊆ [1,N],
there exists M ≥ max(N, Mε) and B ⊆ [N+1, M] with A ∪ B Sidon and
|A ∪ B| ≥ (1-ε)√M.

## Status

This is equivalent to **Erdős Problem 44** on extending Sidon (B₂) sets to near-optimal
density. It remains **open** in the mathematical literature.

## Counterexample Search Results

### Computational Search (Small Parameters)

Greedy extension of various Sidon sets A ⊆ [1,N] to [1,M]:

| Starting Set A | N | M | |A∪B| | √M | Ratio |
|---|---|---|---|---|---|
| {1,2,4,8,13} (greedy) | 20 | 21 | 6 | 4.58 | **1.31** |
| {1,2,4,8,13} | 20 | 100 | 11 | 10.0 | 1.10 |
| {1,2,4,8,13} | 20 | 200 | 14 | 14.1 | 0.99 |
| {1,2,4,8,13} | 20 | 500 | 20 | 22.4 | 0.89 |
| {1,2,4,8,13,21,31,45} (greedy) | 50 | 200 | 14 | 14.1 | 0.99 |
| {1,2,4,8,13,21,31,45} | 50 | 500 | 20 | 22.4 | 0.89 |
| {1,2,4,8,13,21,31,45} | 50 | 1000 | 27 | 31.6 | 0.85 |
| {1,2} | 2 | 50 | 8 | 7.07 | 1.13 |
| {1,2} | 2 | 100 | 11 | 10.0 | 1.10 |
| {1,2} | 2 | 200 | 14 | 14.1 | 0.99 |
| {1,2,5,14} | 14 | 80 | 10 | 8.94 | 1.12 |

**Key finding**: For every tested Sidon set A and every ε > 0 tested, there exists
some M where the greedy extension achieves ratio ≥ 1-ε. The best ratio is typically
achieved at small M (near N), where |A|/√M is largest. No counterexample was found.

### Parameter Extreme Analysis

#### Extreme 1: ε → 0⁺
For very small ε, we need |A∪B| ≈ √M, which is near the maximum possible Sidon set
size. This requires Singer-type algebraic constructions achieving density → 1, which
are known to exist but hard to formalize.

#### Extreme 2: ε ≥ 1
**Trivially true**: (1-ε)√M ≤ 0 ≤ |A∪B|. Take B = ∅. This case is proved in the
formalization (`erdos_44_trivial_case`).

#### Extreme 3: A = ∅ (empty Sidon set)
Need a Sidon set B ⊆ [N+1, M] with |B| ≥ (1-ε)√M. Reduces to existence of
near-optimal Sidon sets in large intervals.

#### Extreme 4: A = {1} (singleton)
Mixed sum constraint: need 1+b ≠ b₁+b₂ for b,b₁,b₂ ∈ B. Analysis shows this
constraint is mild for M >> N (≈ O(1) violations to fix).

#### Extreme 5: A maximal Sidon set in [1,N]
For |A| ≈ √N: take M = N, B = ∅. Then |A|/√N ≈ 1 > 1-ε. **Works for all ε > 0.**
This case is proved in the formalization (`erdos_44_large_A_case`).

### Why No Counterexample Exists (Heuristic Argument)

The theorem allows M to be chosen freely (existentially quantified). For any Sidon
set A ⊆ [1,N]:

1. If |A| ≥ (1-ε)√N: take M = N, B = ∅. Done.
2. If |A| is small: take M >> N. The "damage" from A (creating mixed sum
   constraints) is bounded by O(|A|² · √M) ≈ O(N · √M), which is negligible
   compared to √M for the right choice of M.

The probabilistic argument (alteration method) suggests that for M ≈ C·N²/ε² (with
C sufficiently large), a Sidon extension B of size ≈ √M can be found after removing
O(N) conflicting elements, leaving |B| ≈ √M - O(N) ≈ √M for M >> N².

## Construction That Works (Partial Result)

The **spacing construction** B = {(k+2)(N+1) : k ∈ S'} (where S' is any Sidon set)
gives A ∪ B that is provably Sidon for ANY Sidon set A ⊆ [1,N], because:

1. All differences of B are multiples of (N+1), avoiding A-differences
2. Triple sums b₁+b₂-b₃ = (k₁+k₂-k₃+2)(N+1) can never be in [1,N]
3. min(B) = 2(N+1) > 2N-1, avoiding case 8 collisions

**Limitation**: This construction achieves density only 1/√(N+1), which suffices
for ε ≥ 1 - 1/√(N+1) but not for smaller ε.

## Conclusion

**No counterexample was found** for any parameter combination. The statement is
believed to be true based on:
- Computational evidence for small parameters
- Probabilistic heuristic arguments
- Known Sidon set extension results in the literature

The formal proof requires **Singer's theorem** (existence of near-optimal Sidon sets
from perfect difference sets) or an equivalent deep result from additive combinatorics,
which is beyond current Mathlib coverage.

The `sorry` in the main theorem reflects the **open problem** status of Erdős Problem 44.
Helper lemmas for the trivial cases (ε ≥ 1, large A) are fully proved.
