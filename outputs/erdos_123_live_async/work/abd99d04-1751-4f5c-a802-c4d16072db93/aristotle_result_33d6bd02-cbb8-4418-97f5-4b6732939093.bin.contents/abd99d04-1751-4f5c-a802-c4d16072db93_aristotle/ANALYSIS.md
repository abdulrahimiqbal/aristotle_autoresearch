# Erdős Problem 123 — Perturbation Analysis

## Experiment Summary

**Modification applied:** `{"assumption": "summands are distinct", "operation": "remove"}`

## 1. Blocker Report: Does removing "summands are distinct" block the proof?

**Short answer: No.** Removing the explicit "summands are distinct" assumption creates **no new blocker**. The distinctness condition is already structurally enforced by the `Finset ℕ` type used in the formalization.

### Detailed explanation

The current definition of `IsDComplete` uses `Finset ℕ`:
```lean
def IsDComplete (A : Set ℕ) : Prop :=
  ∀ᶠ n : ℕ in atTop, ∃ s : Finset ℕ,
    (↑s : Set ℕ) ⊆ A ∧ IsDivisionAntichain s ∧ s.sum id = n
```

`Finset ℕ` enforces element uniqueness at the type level — a `Finset` is internally a `Multiset` with a `Nodup` proof (`s.nodup : s.val.Nodup`). Therefore:

- **Before the perturbation:** An explicit "summands are distinct" hypothesis was present but **redundant** — it was already guaranteed by the `Finset` carrier.
- **After the perturbation:** Removing the redundant hypothesis changes nothing. The theorem statement is logically identical.

If the intent were to genuinely allow repeated summands, the formalization would need to replace `Finset ℕ` with `Multiset ℕ` (and adjust `IsDivisionAntichain` accordingly). Under that reading, allowing repetitions would make the theorem **strictly easier** (more representations available), so it would still not introduce a blocker. However, the antichain condition `x ≠ y → ¬ x ∣ y` becomes ill-defined for multisets with duplicate elements, so the `Finset` formulation is the mathematically correct one.

**The real blocker** is the mathematical depth of the theorem itself: showing that antichain subset sums from `PowTripleSet(a, b, c)` cover all sufficiently large integers requires a sophisticated construction that goes beyond what current automated provers can produce.

## 2. What was proved

All helper lemmas were fully formalized:

| Lemma | Status | Purpose |
|-------|--------|---------|
| `one_mem_PowTripleSet` | ✅ Proved | 1 ∈ PowTripleSet |
| `PowTripleSet_pos` | ✅ Proved | Elements are positive |
| `a_mem_PowTripleSet` | ✅ Proved | Generator membership |
| `b_mem_PowTripleSet` | ✅ Proved | Generator membership |
| `c_mem_PowTripleSet` | ✅ Proved | Generator membership |
| `PowTripleSet_mul_closed` | ✅ Proved | Multiplicative closure |
| `PowTripleSet_dvd_iff` | ✅ Proved | **Key structural result:** divisibility ↔ coordinate-wise ≤ |
| `PowTripleSet_finite_le` | ✅ Proved | Bounded subsets are finite |
| `frobenius_two_coprime` | ✅ Proved | Sylvester–Frobenius for two coprime integers |
| `cross_family_incomparable` | ✅ Proved | A-family vs B-family incomparability |
| `singleton_antichain` | ✅ Proved | Vacuous antichain condition |
| `pair_antichain` | ✅ Proved | Two-element antichains |
| `erdos_123_d_complete_sequences` | ❌ Sorry | Main theorem — deep result |

## 3. Discovery Question: Which special cases transfer?

### The key reformulation

The divisibility structure of `PowTripleSet(a, b, c)` is completely characterized by `PowTripleSet_dvd_iff`:

> `a^i · b^j · c^k ∣ a^{i'} · b^{j'} · c^{k'}` **if and only if** `i ≤ i' ∧ j ≤ j' ∧ k ≤ k'`

This means the divisibility poset of `PowTripleSet(a, b, c)` is **isomorphic to (ℕ³, ≤)** as a partial order, regardless of the specific values of `a, b, c` (as long as they are pairwise coprime and > 1). The values only affect the *weights* (the actual numerical values of elements), not the *comparability structure*.

### Obstruction reformulation

The d-completeness question reduces to:

> **For which weight functions w : ℕ³ → ℕ given by w(i,j,k) = a^i · b^j · c^k, does every sufficiently large n have a representation n = Σ_{v ∈ S} w(v) where S is a finite antichain in (ℕ³, ≤)?**

### Special cases that transfer

1. **Two-family decomposition (proved as infrastructure):** Elements split into:
   - **A-family:** `{a^i · c^k : i ≥ 1}` (b-exponent = 0)
   - **B-family:** `{b^j · c^l : j ≥ 1}` (a-exponent = 0)

   By `cross_family_incomparable`, any A-element is incomparable with any B-element. This structure is **universal** — it transfers to ALL valid triples. The union of any A-antichain and any B-antichain is automatically a division antichain.

2. **Frobenius representation (proved as infrastructure):** For any coprime pair (a, b) with a, b > 1, every n ≥ (a−1)(b−1) decomposes as n = xa + yb. This threshold is **triple-independent** (depends only on two generators at a time).

3. **Staircase antichains transfer universally:** For any M ≥ 2, the set `{a^i · c^{M-i} : 1 ≤ i ≤ M}` is an antichain of size M−1 in PowTripleSet. The antichain property follows purely from the poset structure (coordinate comparison) and transfers to all triples.

4. **Subset sum completeness conditions depend on the ratio:** The subset sums of a staircase `{a^i · c^{M-i}}` cover a contiguous interval only when the consecutive ratio `a/c` satisfies `max(a/c, c/a) ≤ 2`. This is the key parameter-dependent condition:
   - **Favorable triples** (e.g., (2, 3, 5) where all ratios < 2): Staircase subset sums directly cover intervals, and the two-family sumset covers all large integers.
   - **Unfavorable triples** (e.g., (2, 3, 7) where 7/2 > 2): Single staircases have gaps, requiring multi-scale constructions combining different staircase sizes.

5. **The case a = b:** Not applicable here (requires a ≠ b for coprimality with a, b > 1), but the "near-equal" case where a/b ≈ 1 is most tractable.

### Transfer principle

The following results proved for ANY specific triple `(a₀, b₀, c₀)` automatically transfer to ALL triples:

- **Antichain structure lemmas** — because the poset (ℕ³, ≤) is universal
- **Cross-family incomparability** — because it depends only on coprimality
- **Frobenius thresholds** — because they depend only on pairwise coprimality
- **Staircase constructions** — because they use only the poset structure

What does **NOT** transfer automatically:

- **Subset sum coverage** — because the actual element values (weights) determine which sums are achievable
- **Gap-filling arguments** — because gap sizes depend on the specific ratios a/b, a/c, b/c
- **Specific numerical verifications** — e.g., "every n ∈ [100, 200] has an antichain representation" is triple-specific

### Recommended proof strategy for the general theorem

1. Establish the two-family decomposition (done: `cross_family_incomparable`).
2. For each family independently, show that subset sums of multi-scale staircases achieve sufficient density.
3. Show that the sumset of two sufficiently dense subsets covers all large integers.
4. The density argument requires showing that for each residue class mod `lcm(a,c)` (for A-family) and mod `lcm(b,c)` (for B-family), there is a staircase subset sum in that class.
5. Since `gcd(a,c) = 1` and `gcd(b,c) = 1`, the multiplicative orders provide the necessary residue coverage.

Steps 2–5 constitute the remaining mathematical content of the proof.
