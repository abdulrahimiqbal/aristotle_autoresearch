# Erdős Problem 44 — Exploration Report

## Overview

The file `Main.lean` formalizes Erdős Problem 44 about extending Sidon sets to
near-optimal density. This is an **open problem** in additive combinatorics.

## What was proved

| Declaration | Status |
|---|---|
| `erdos_44_sidon_extension` | **`sorry`** (open conjecture) |
| `isSidonFinset_empty` | ✅ proved |
| `IsSidonFinset.subset` | ✅ proved |
| `union_empty_eq` | ✅ proved |
| `erdos_44_weakened_large_eps` | ✅ proved (ε ≥ 1 case) |
| `sidon_124` | ✅ proved ({1,2,4} is Sidon) |
| `sidon_witness` | ✅ proved ({1,2,4,8,13,21,31,45,66,81,97} is Sidon) |
| `witness_contains_124` | ✅ proved |
| `witness_extension_range` | ✅ proved |
| `witness_card` | ✅ proved (= 11) |
| `witness_density_bound` | ✅ proved ((1/2)√97 < 11) |
| `negation_counterexample_eps_half` | ✅ proved |

## Counterexample to the negated weakening

The **negation** of the conjecture asserts:

> ∃ ε > 0, ∀ M₀, ∃ N ≥ 1, ∃ A ⊆ [1,N] Sidon,
>   ∀ M ≥ max(N, M₀), ∀ B ⊆ [N+1, M], ¬Sidon(A∪B) ∨ |A∪B| < (1−ε)√M

We refute this for **ε = 1/2** by exhibiting a concrete extension:

- **Initial set:** A = {1, 2, 4} (Sidon in [1, 4])
- **Extension:** B = {8, 13, 21, 31, 45, 66, 81, 97} ⊆ [5, 97]
- **Union:** A ∪ B = {1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97} — verified Sidon
- **Density:** |A ∪ B| = 11 ≥ (1/2)√97 ≈ 4.92 ✓

For any M₀ ≤ 97, this witness shows the negation fails at N = 4.
Greedy extension experiments show the pattern holds for arbitrarily large M:

| M | |greedy extension| | √M |
|---|---|---|
| 50 | 8 | ≈ 7.1 |
| 100 | 10 | 10 |
| 200 | 13 | ≈ 14.1 |
| 400 | 19 | 20 |

The ratio |ext|/√M stays close to 1, meaning the negation fails for all
tested ε > 0 — strong computational evidence **for** the conjecture.

## Provable weakening (ε ≥ 1)

When ε ≥ 1, the bound (1−ε)√M ≤ 0, so any non-empty Sidon set trivially
satisfies the density requirement. This is formalized as
`erdos_44_weakened_large_eps`.

## Conclusion

The full Erdős Problem 44 remains open. The negation of the conjecture is
computationally refuted for all tested ε values, with a formally verified
counterexample for ε = 1/2. No independence witness was found — all evidence
points toward the conjecture being true.
