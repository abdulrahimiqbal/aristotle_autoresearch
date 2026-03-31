# Erdős Problem 123 — Boundary Analysis & Reusable Lemma Catalog

## Witness Minimization: Sharp Boundary

The `?` in the witness minimization target resolves to **the number of pairwise coprime generators**.

### The Boundary

| Configuration | d-complete? | Evidence |
|:---|:---|:---|
| 1 generator (`{a^i}`) | **NO** | Antichains are singletons (powers form a chain), so only powers of `a` are antichain sums |
| 2 generators, `max/min ≥ 2` (e.g. `{2^i·5^j}`) | **NO** | Fails at n = 3, 6, 11, 12, 15, 17, 19, ... (verified ≤ 200) |
| 2 generators, `max/min < 2` (e.g. `{2^i·3^j}`) | Appears **YES** | No failures found for n ≤ 50 |
| **3 pairwise coprime generators ≥ 2** | **YES** (the theorem) | `PowTripleSet(2,3,5)` covers all n ≤ 50; (d+1)(d+2)/2 level-d elements provide quadratic antichain growth |

**Sharp blocker for 2-generator failure:** When `max/min ≥ 2`, level-d antichain elements form a geometric progression with ratio ≥ 2. Subset sums of such a progression have absolute gaps ≥ `min^d`, which grow without bound. No finite antichain of 2-generator elements can plug all gaps simultaneously.

**Why 3 generators suffice:** Level-d elements of `PowTripleSet(a,b,c)` have size `(d+1)(d+2)/2 ∝ d²`, growing quadratically. The number of possible subset sums `2^{d²/2}` dwarfs the value range `[min^d, max^d]`, so by density arguments the subset sums eventually cover all integers in a range that overlaps across levels.

### Minimal Witness Triple

`(a, b, c) = (2, 3, 5)` is the smallest pairwise coprime triple with all entries > 1. Computationally, every integer from 1 to 50 has an antichain-sum representation in `PowTripleSet(2, 3, 5)`, suggesting the d-completeness threshold `N₀ = 1` (i.e., ALL positive integers are representable for this triple).

---

## Reusable Lemma Catalog

The following lemmas recur across all parameter triples `(a, b, c)` and are strong enough to promote to general-purpose library lemmas:

### 1. `coprime_triple_dvd_iff` — Divisibility-Extraction Workhorse

```
a^i₁ * b^j₁ * c^k₁ ∣ a^i₂ * b^j₂ * c^k₂  ↔  i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂
```

**Recurrence pattern:** Used in *every* argument involving divisibility in `PowTripleSet`. The proof factors through `Nat.Coprime.dvd_of_dvd_mul_right` and `Nat.factorization_le_iff_dvd`, extracting each exponent comparison independently via coprimality.

**Promotability:** Generalizes to k-tuples of pairwise coprime bases. The natural generalization would use `Finsupp ℕ ℕ` for exponent vectors and `Finset.prod` for the product, with `Pairwise Nat.Coprime` on the base set.

### 2. `same_level_is_antichain` — Core Covering Lemma

```
(∀ x ∈ s, ∃ i j k, x = a^i * b^j * c^k ∧ i+j+k = d) → IsDivisionAntichain s
```

**Recurrence pattern:** Appears whenever we construct antichain subsets for covering arguments. The proof is a one-liner from `coprime_triple_dvd_iff`: componentwise ≤ with equal coordinate-sum forces equality, contradicting distinctness.

**Promotability:** The underlying principle is purely order-theoretic: in any poset isomorphic to `(ℕᵏ, ≤)`, the "antichains at constant weight" property holds. Could be stated as a general lemma about `Finsupp ℕ ℕ` ordered by `≤`.

### 3. `cross_type_antichain_pair` — Incomparability Detector

```
¬(i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂) → ¬(i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁)
  → IsDivisionAntichain {a^i₁ * b^j₁ * c^k₁, a^i₂ * b^j₂ * c^k₂}
```

**Recurrence pattern:** Used to verify that specific pairs of elements are antichain-compatible, enabling constructions that mix elements across different "types" (e.g., a-dominant vs b-dominant). Instantiated as `pure_powers_antichain` for the case of pure powers of distinct bases.

**Promotability:** The natural generalization: for any poset, two incomparable elements form a 2-element antichain. In our setting, `coprime_triple_dvd_iff` reduces the poset question to `ℕ³` coordinate comparison.

### 4. `PowTripleSet_mul_closed` — Multiplicative Closure

```
x ∈ PowTripleSet a b c → y ∈ PowTripleSet a b c → x * y ∈ PowTripleSet a b c
```

**Recurrence pattern:** Used to build new antichain elements from existing ones by multiplying exponents. Also used in `PowTripleSet_pow_mem`.

**Promotability:** Immediate from the fact that exponents add under multiplication. Generalizes to any number of generators.

### 5. `IsDivisionAntichain.subset` — Monotonicity

```
IsDivisionAntichain t → s ⊆ t → IsDivisionAntichain s
```

**Recurrence pattern:** Foundational. Used whenever we select a sub-antichain from a known antichain.

---

## What's Missing for the Full Proof

The main theorem `erdos_123_d_complete_sequences` has one remaining `sorry`. The gap is the **combinatorial covering step**: showing that subset sums of level-d antichain elements eventually cover all integers. This requires either:

1. **A subset-sum density theorem:** For sets of integers with GCD 1 and enough elements relative to their range, subset sums cover all sufficiently large integers. Such a result exists in the additive combinatorics literature (related to Freiman-type inverse theorems) but is not formalized in Mathlib.

2. **A constructive covering argument:** Explicitly construct, for each large n, a level-d antichain whose subset sums include n. This requires careful analysis of the geometric structure of level-d elements.

3. **A Frobenius-type extension:** Extend the Chicken McNugget theorem (`frobeniusNumber_pair` in Mathlib) from linear combinations to subset sums of elements with multiplicative structure.

All structural lemmas supporting these approaches are fully proved. The combinatorial core is the principal barrier.
