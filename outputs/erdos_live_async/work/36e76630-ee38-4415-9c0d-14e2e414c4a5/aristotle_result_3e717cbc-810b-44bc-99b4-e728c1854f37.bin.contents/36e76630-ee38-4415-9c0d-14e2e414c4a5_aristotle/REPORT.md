# Erdős Problem 44 — Analysis Report

## Problem Statement

Erdős Problem 44 asks whether every Sidon (B₂) set in [1,N] can be extended to a
near-optimal Sidon set in [1,M] for some sufficiently large M. Formally:

> For any ε > 0, there exists Mε such that for all N ≥ 1 and all Sidon sets
> A ⊆ [1,N], there exists M ≥ max(N, Mε) and B ⊆ [N+1, M] with A∪B Sidon
> and |A∪B| ≥ (1-ε)√M.

**This is an open problem.** The sorry on `erdos_44_sidon_extension` cannot be
eliminated without resolving the conjecture.

## What Was Proved

All sorries except the main conjecture have been filled:

| Theorem | Status |
|---------|--------|
| `isSidon_empty` | ✅ Proved |
| `isSidon_singleton` | ✅ Proved |
| `isSidon_pair` | ✅ Proved |
| `sidon_witness` ({1,2,5,11,19}) | ✅ Proved |
| `sidon_card_bound` (|A|·(|A|-1)/2 ≤ 2N) | ✅ Proved |
| `sidon_extend_by_one` | ✅ Proved |
| `minimal_variant_extension` | ✅ Proved |
| `sidon_card_lt_sqrt` (|A| < 2√N + 1) | ✅ Proved |
| `superdensity_variant_false` | ✅ Proved |
| `erdos_44_sidon_extension` | ❌ Open problem (sorry) |

## Counterexample / Independence Analysis for the Minimal Variant

### Minimal variant (proved true)
The **minimal non-trivial variant** of Erdős 44 asks: can every Sidon set be extended
to a strictly larger Sidon set? This is `minimal_variant_extension` and is **proved
true** — any Sidon set A can be extended by adding a sufficiently large element
(specifically, x = 2·max(A) + 1 works).

### Counterexample to the super-density strengthening
The theorem `superdensity_variant_false` shows that the conjecture **cannot be
improved** to ask for |A∪B| ≥ c·√M with any c > 2. This follows from the
Sidon counting bound: the number of distinct pairwise sums C(|A|,2) must fit
in {2,...,2N}, giving |A| < 2√N + 1.

### Computational exploration of the bounded-M variant
When M is restricted to M ≤ C·N for fixed C (instead of being existentially
chosen), greedy extension experiments show:

| Starting set | N | M | |A∪B| | |A∪B|/√M |
|-------------|---|---|-------|---------|
| ∅ | 0 | 500 | 20 | 0.89 |
| greedy(20) | 20 | 500 | 20 | 0.89 |
| greedy(50) | 50 | 1000 | 27 | 0.85 |
| greedy(100) | 100 | 2000 | 35 | 0.78 |

The ratio |A∪B|/√M for greedy extension falls as N grows, suggesting that
greedy methods alone cannot achieve the (1-ε) bound. However, optimal
(non-greedy) constructions might do better — this is precisely the content
of the open conjecture.

### Independence considerations
The conjecture sits between two extremes:
1. **Trivially true**: "Every Sidon set can be extended" (`minimal_variant_extension`)
2. **Provably false**: "Sidon sets can achieve density > 2√N" (`superdensity_variant_false`)

A formal proof of the full conjecture would require formalizing:
- Singer perfect difference sets over GF(q)
- The probabilistic method for Sidon constructions
- Additive combinatorics extension machinery

None of these are currently available in Mathlib.
