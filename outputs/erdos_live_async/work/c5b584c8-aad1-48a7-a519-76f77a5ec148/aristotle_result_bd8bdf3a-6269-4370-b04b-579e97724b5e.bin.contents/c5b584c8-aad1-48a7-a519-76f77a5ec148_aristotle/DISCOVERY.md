# Discovery: D-Completeness Boundary Cases

## Question

Which d-completeness boundary cases fail because interval-style coverage cannot be
upgraded to a divisibility antichain, and what is the sharpest witness?

## Answer

The **exact boundary** is **d = 1** (a single base), and the **sharpest witness** is
the set **S = {2^i : i ∈ ℕ} = {1, 2, 4, 8, 16, …}**.

### Why interval coverage holds

For any single base p ≥ 2, the geometric set {p^i : i ∈ ℕ} places an element in
every interval [p^k, p^{k+1}). In particular, {2^i} achieves the *densest possible*
geometric coverage: every interval [n, 2n] for n ≥ 1 contains 2^⌊log₂ n⌋.

### Why divisibility antichains fail

A divisibility antichain is a set where no element divides any other. In {p^i}, every
pair p^i, p^j with i < j satisfies p^i | p^j. The set is a **total chain** under
divisibility — its maximal antichain has size exactly **1**.

This is the maximal degeneracy: despite perfect interval coverage, the divisibility
structure is trivial (linear order).

### Why the boundary is sharp

With **two coprime bases** a, b (both ≥ 2, gcd(a,b) = 1), elements a^i and b^j
(for i, j ≥ 1) are divisibility-incomparable: neither a^i | b^j nor b^j | a^i
(since gcd(a,b) = 1 and both are ≥ 2). This immediately creates antichains of
unbounded size:

  {a, b, a², b², a³, b³, …}

contains the antichain {a^i, b^j} for any i, j ≥ 1. More generally, the set
{a^i · b^j · c^k} for three pairwise coprime bases contains antichains of
size Θ((log N)²) among elements ≤ N.

### Summary table

| Bases (d) | Interval coverage | Max antichain size | D-complete? |
|-----------|-------------------|-------------------|-------------|
| d = 1     | ✓                 | 1 (total chain)   | Only if base = 2 |
| d = 2     | ✓                 | Unbounded         | Not always (e.g., {3^i · 5^j} fails at 22) |
| d = 3     | ✓                 | Unbounded         | ✓ (Erdős theorem) |

The transition from trivial (size-1) antichains to unbounded antichains occurs
at d = 2. The d-completeness transition (for pairwise coprime bases ≥ 2) occurs
at d = 3, where three independent multiplicative dimensions provide enough density
to fill all residue classes.
