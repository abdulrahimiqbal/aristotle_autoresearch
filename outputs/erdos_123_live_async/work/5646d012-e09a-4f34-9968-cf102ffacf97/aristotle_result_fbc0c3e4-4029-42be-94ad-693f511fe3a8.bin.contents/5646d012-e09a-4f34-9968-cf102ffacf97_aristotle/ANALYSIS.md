# Erdős Problem 123: Adversarial Analysis

## Problem Statement

For pairwise coprime natural numbers $a, b, c > 1$, is the multiplicative semigroup
$S = \{a^i \cdot b^j \cdot c^k : i, j, k \in \mathbb{N}\}$ *d-complete*?

A set $A \subseteq \mathbb{N}$ is **d-complete** if every sufficiently large integer $n$
can be written as a sum of distinct elements from $A$ that form a **divisibility antichain**
(no element divides another).

## Status

**Open problem.** The main theorem `erdos_123_d_complete_sequences` remains as `sorry`.
All 10 supporting infrastructure lemmas have been fully proved.

## Proved Infrastructure

| Lemma | Statement | Role |
|-------|-----------|------|
| `div_implies_exp_le` | $a^{i_1} b^{j_1} c^{k_1} \mid a^{i_2} b^{j_2} c^{k_2} \implies (i_1,j_1,k_1) \leq (i_2,j_2,k_2)$ | Reduces antichain condition from $\mathbb{N}$ to $\mathbb{N}^3$ |
| `exp_le_implies_div` | Componentwise $\leq$ implies divisibility | Reverse direction |
| `singleton_antichain` | Any element of PowTripleSet gives a trivial antichain sum | Base case |
| `coprime_pair_antichain` | Coprime elements $> 1$ form an antichain | Transfer lemma |
| `coprime_pow_of_coprime` | $\gcd(a,b) = 1 \implies \gcd(a^i, b^j) = 1$ | Coprimality lifts |
| `pure_powers_not_dvd` | $\gcd(a,b) = 1, a,b > 1 \implies a^i \nmid b^j$ for $i,j > 0$ | Incomparability |
| `pairwise_coprime_antichain` | Pairwise coprime elements $> 1$ form an antichain | Key transfer |
| `sylvester_frobenius` | Chicken McNugget theorem: $\forall^{\infty} n,\ \exists x,y \geq 0: n = xa + yb$ | Additive coverage |
| `IsDComplete.mono` | $A \subseteq B \land A$ d-complete $\implies B$ d-complete | Monotonicity |
| `antidiag_antichain` | Anti-diagonal elements $\{a^i b^{K-i} : 0 \leq i \leq K\}$ form an antichain | Construction tool |

## Adversarial Analysis of the "Unknown" Blocker

### What the blocker IS

The core obstruction is the **density gap problem**: constructing antichain subsets
whose *sums* hit every large integer.

Individual building blocks exist:
- **Antichains are plentiful**: Anti-diagonals $\{a^i b^{K-i}\}$ give antichains of arbitrary size.
- **Coprimality gives antichains for free**: Any set of elements with disjoint prime supports is an antichain.
- **Additive coverage exists**: Sylvester-Frobenius guarantees linear combinations cover all large integers.

The gap: *antichain sums* are a structured subset of *all sums*. The subset sums of an
anti-diagonal $\{a^0 b^K, a^1 b^{K-1}, \ldots, a^K b^0\}$ give $2^{K+1} - 1$ possible
values, but these values are not consecutive. Covering all large integers requires either:

1. **Multi-level mixing**: Combining elements from different anti-diagonals (but cross-level
   elements may be comparable).
2. **Three-generator flexibility**: Using the third generator $c$ to "fill gaps" left by
   the two-generator anti-diagonal construction.
3. **Fundamentally different construction**: Perhaps using elements with mixed exponent
   signatures that don't lie on any single anti-diagonal.

### What the blocker is NOT

The blocker is *not* a structural limitation of the problem. The proved lemmas show:
- The antichain condition is well-behaved (equivalent to componentwise incomparability).
- Coprimality provides a robust source of antichains.
- The set PowTripleSet is rich enough (infinite, multiplicatively closed, contains
  all pure powers).

## Transfer Principles: Special Cases → General Triples

### Which special cases transfer?

1. **Pure coprimality transfer** (`pairwise_coprime_antichain`):
   Any proof that constructs antichain sums using elements with disjoint prime supports
   transfers immediately to all pairwise coprime triples. This is because the coprimality
   of the generators is the *only* property used.

2. **Anti-diagonal transfer** (`antidiag_antichain`):
   The anti-diagonal construction works for any two coprime bases. A proof based on
   anti-diagonal subset sums for $(a_0, b_0)$ would transfer to any $(a, b)$ with
   the same coprimality structure, though the specific achievable sums change.

3. **Monotonicity transfer** (`IsDComplete.mono`):
   D-completeness of $\{a^i b^j c^k\}$ for specific $(a_0, b_0, c_0)$ transfers to
   $(a_0, b_0, c_0)$ trivially (identity), and more interestingly, any triple whose
   PowTripleSet *contains* the original one inherits d-completeness.

4. **Sylvester-Frobenius transfer** (`sylvester_frobenius`):
   The additive coverage result works for all coprime pairs. A proof that combines
   Frobenius coverage with antichain refinement would transfer to all triples where
   the two chosen generators are coprime.

### What does NOT transfer

- **Computational verifications**: Checking d-completeness for $(2, 3, 5)$ up to
  $n = N$ does not transfer to other triples, as the achievable sums depend on the
  specific generators.

- **Base-specific constructions**: Proofs relying on binary representation (when $a = 2$)
  don't directly transfer to triples where no generator is 2.

## Reformulating the Obstruction

The obstruction can be reformulated as:

> **Gap-Filling Problem**: For coprime $a, b > 1$, does the set of "antichain-sum-reachable"
> integers from $\{a^i b^j : i, j \geq 0\}$ have density 1 in $\mathbb{N}$? And if not,
> does adding a third coprime generator $c$ fill the remaining gaps?

This reformulation suggests three attack vectors:

1. **Density argument**: Show the antichain sumset has positive lower density, then use
   the third generator to cover remaining residue classes.

2. **Greedy algorithm**: Show a greedy construction (always pick the largest antichain-compatible
   element ≤ remaining target) terminates for all large $n$.

3. **Mixed-base representation**: Develop a "mixed radix" system using all three generators
   simultaneously, analogous to how $\{2^i 3^j 5^k\}$ provides a rich digit system.

Each of these would benefit from new Mathlib infrastructure around subset sum density
and additive combinatorics of multiplicative sets.
