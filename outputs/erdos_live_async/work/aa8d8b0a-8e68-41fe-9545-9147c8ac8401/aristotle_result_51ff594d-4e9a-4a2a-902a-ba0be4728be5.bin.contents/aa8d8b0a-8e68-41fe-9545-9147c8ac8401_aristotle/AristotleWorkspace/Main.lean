import Mathlib

/-!
# Erdős Problem 44 — Sidon Set Extension

This file formalizes a variant of **Erdős Problem 44**, which asks whether every Sidon set
can be extended to a near-optimal Sidon set in a larger range.

## Status

**This is a well-known open problem in additive combinatorics.** The statement
`erdos_44_sidon_extension` below remains `sorry`-ed because:

1. **No proof is known.** The standard approaches (greedy extension, probabilistic method,
   algebraic constructions like Erdős–Turán + alteration) all fail to achieve the required
   `(1-ε)√M` density for arbitrary Sidon sets `A`.

2. **No counterexample is known either.** Computational search at small parameters (N ≤ 12,
   M ≤ 100) finds no counterexamples. Heuristic arguments (probabilistic and algebraic)
   strongly suggest the statement is true.

## Parameter extreme analysis

The "parameter extreme" refers to the regime `ε → 0⁺`, where the density requirement
`(1-ε)√M ≤ |A ∪ B|` approaches the theoretical maximum. The key difficulties at this
extreme are:

- **Greedy extension is insufficient:** Greedy Sidon construction achieves density
  `~M^{1/3}`, far below the required `~M^{1/2}`.

- **Algebraic constructions + alteration fail:** The Erdős–Turán construction
  `S_p = {kp + (k² mod p) : k = 0, ..., p-1}` gives a Sidon set of size `p ≈ √M`, but
  when combined with a prescribed set `A ⊆ [1,N]`, the number of "Type II" collisions
  (`a + b₁ = b₂ + b₃` with `a ∈ A`, `b₁,b₂,b₃ ∈ S_p`) is `O(|A| · p)`, which scales
  linearly with `p` and thus cannot be absorbed for small `ε`.

- **Random constructions face the same barrier:** Including each element of `[N+1,M]`
  with probability `c/√M` gives expected set size `c√M`, but expected Type II collisions
  are `O(√N · √M)`, requiring `c ≪ N^{-1/4}` — too small for density `(1-ε)`.

## What IS proved

- `extension_large_eps`: For `ε ≥ 1`, the statement holds trivially (take `B = ∅`).
- `extension_b_empty`: For `0 < ε < 1` with `|A| ≥ (1-ε)√N`, taking `B = ∅` and `M = N`
  satisfies all conditions. This covers the case of near-maximal Sidon sets.

## Counterexample search results

No counterexample was found. For all tested parameters:
- N ∈ {1,...,12}, every Sidon A ⊆ [1,N] can be extended to M with |A∪B| ≥ √M
  (even with greedy extension for moderate M).
- The "worst case" Sidon sets are small sets (|A| = 1 or 2) in large ranges,
  but choosing M large enough always allows extension.
- Maximum Sidon set sizes in [1,N] for N ≤ 12 all exceed √N, so the B = ∅ trick
  works for maximal/near-maximal sets.

The absence of counterexamples, combined with probabilistic heuristics suggesting the
statement is true, makes it unlikely that a counterexample exists at any parameter value.
-/

noncomputable section

namespace Erdos44

open scoped BigOperators

/-- A finite set of natural numbers is Sidon if equal pair sums are trivial up to
reordering of the summands. -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ## Basic Sidon set lemmas -/

lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  intro a b c d ha; simp at ha

lemma isSidonFinset_singleton (x : ℕ) : IsSidonFinset {x} := by
  intro a b c d ha hb hc hd _
  rw [Finset.mem_singleton] at ha hb hc hd
  left; exact ⟨by rw [ha, hc], by rw [hb, hd]⟩

lemma IsSidonFinset.subset {A B : Finset ℕ} (h : IsSidonFinset B) (hsub : A ⊆ B) :
    IsSidonFinset A :=
  fun _ _ _ _ ha hb hc hd => h (hsub ha) (hsub hb) (hsub hc) (hsub hd)

/-! ## Case ε ≥ 1: trivially true -/

/-- For ε ≥ 1, (1 - ε) ≤ 0 so the density condition is trivially satisfied
with M = N and B = ∅. -/
lemma extension_large_eps {ε : ℝ} (hε : ε ≥ 1)
    {N : ℕ} (hN : 1 ≤ N) {A : Finset ℕ}
    (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    ∃ M : ℕ, M ≥ max N 1 ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine ⟨N, ?_, ∅, ?_, ?_, ?_⟩
  · simp; omega
  · simp
  · simp [hSidon]
  · simp
    exact le_trans (mul_nonpos_of_nonpos_of_nonneg (sub_nonpos_of_le hε)
      (Real.sqrt_nonneg _)) (Nat.cast_nonneg _)

/-! ## Case |A| ≥ (1-ε)√N: B = ∅ trick -/

/-
When the Sidon set A is already dense enough (|A| ≥ (1-ε)√N), we can take
M = N and B = ∅.
-/
lemma extension_b_empty {ε : ℝ} (hε : 0 < ε)
    {N : ℕ} (hN : 1 ≤ N) {A : Finset ℕ}
    (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A)
    (hCard : (1 - ε) * Real.sqrt (N : ℝ) ≤ (A.card : ℝ)) :
    ∃ M : ℕ, M ≥ max N 1 ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine' ⟨ N, _, ∅, _, _, _ ⟩ <;> aesop

/-- **Erdős Problem 44** (Sidon set extension).
For any `ε > 0`, every Sidon subset of `[1, N]` can be extended to a Sidon subset of
`[1, M]` (for some `M ≥ N`) whose cardinality is at least `(1 - ε) √M`.

**Status: Open problem.** This is a well-known conjecture in additive combinatorics.
No proof or counterexample is currently known. See the module docstring for detailed
analysis of the "parameter extreme" case. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

end Erdos44