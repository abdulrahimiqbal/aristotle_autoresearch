# Erdős Problem 123 — Analysis & Discovery

## Summary of Results

### 1. Negated Weakening: Counterexample Found and Proved

The **weakened** form of Erdős Problem 123 drops the pairwise coprimality hypothesis:

> ∀ a b c : ℕ, 1 < a → 1 < b → 1 < c → IsDComplete (PowTripleSet a b c)

**This is FALSE.** The theorem `negated_weakening` is proved in `AristotleWorkspace.lean`.

**Counterexample:** `a = 2, b = 4, c = 8`.

- `PowTripleSet 2 4 8 = {2^(i+2j+3k) | i,j,k ∈ ℕ} = {2^n | n ∈ ℕ}` (all powers of 2).
- Among powers of 2, every pair satisfies a divisibility relation (`2^i ∣ 2^j` when `i ≤ j`).
- Therefore, the only divisibility antichains in this set are singletons (or empty).
- Only powers of 2 themselves can be represented as antichain sums — the set is NOT d-complete.

### 2. Proved Theorems (sorry-free, verified axioms)

| Theorem | Status |
|---------|--------|
| `powTripleSet_2_4_8_eq` | ✅ Proved |
| `pow2_antichain_singleton` | ✅ Proved |
| `powTripleSet_2_4_8_not_dComplete` | ✅ Proved |
| `negated_weakening` | ✅ Proved |
| `pow2_interval_coverage` | ✅ Proved |
| `pow2_not_dComplete` | ✅ Proved |
| `erdos_123_d_complete_sequences` | ⬚ Open problem (sorry) |

All proved theorems depend only on standard axioms: `propext`, `Classical.choice`, `Quot.sound`.

### 3. Discovery: d-Completeness Boundary Cases

**Question:** Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?

**Answer:**

The failure occurs precisely when the generating set forms a **multiplicative chain** — that is, when all elements are powers of a single base. In this situation:

- **Interval coverage succeeds perfectly:** Every positive integer has a unique binary (or base-b) representation as a sum of distinct powers, giving complete coverage of ℕ.
- **Antichain upgrade fails completely:** Any two distinct elements satisfy a divisibility relation, so antichains are limited to singletons. Only the generators themselves are antichain-representable — a density-zero subset.

**Sharpest witness:** `A = {2^n | n ∈ ℕ}` (equivalently, `PowTripleSet 2 4 8`).

This is the sharpest witness because:

1. **Maximum gap:** The interval coverage gives *all of ℕ⁺*, while antichain coverage gives only *{1, 2, 4, 8, ...}* — a set of natural density zero. The gap is maximal.

2. **Boundary structure:** This corresponds to the case where coprimality fails *maximally* — all three generators share a common prime factor (indeed, they are all powers of 2). As coprimality is restored (e.g., moving from {2, 4, 8} toward {2, 3, 5}), the divisibility structure of the generating set loosens, enabling more antichains and eventually (conjecturally) full d-completeness.

3. **Critical transition:** The boundary between d-complete and non-d-complete sets is determined by whether the generators produce elements with sufficiently "independent" prime factorizations. When gcd(a,b) = gcd(a,c) = gcd(b,c) = 1, elements of `PowTripleSet a b c` have orthogonal factorizations, making it possible to form antichains. When this independence collapses (shared prime factors), the chain structure forces antichain failure.

**Generalization:** For any single prime p, the set `{p^n | n ∈ ℕ}` has perfect interval coverage (base-p representation) but is not d-complete. The case p=2 gives the simplest and sharpest witness. More generally, `PowTripleSet(p^a, p^b, p^c)` for any prime p and positive a, b, c collapses to powers of p and fails d-completeness, while maintaining full interval coverage through p-ary representation.
