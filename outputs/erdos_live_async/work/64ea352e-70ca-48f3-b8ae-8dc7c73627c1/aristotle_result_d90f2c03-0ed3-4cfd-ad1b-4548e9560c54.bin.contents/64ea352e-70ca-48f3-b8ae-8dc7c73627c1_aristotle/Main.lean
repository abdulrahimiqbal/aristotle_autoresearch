/-
Experiment ID: 64ea352e-70ca-48f3-b8ae-8dc7c73627c1
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 21, "target": "most_fragile_variant"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
import Mathlib

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

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**Status**: this remains `sorry`'d because the statement is essentially an open problem
in additive combinatorics — proving it requires either Singer's algebraic construction
of perfect difference sets or a careful probabilistic argument, neither of which is
currently available in Mathlib. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

/-!
## Most fragile variant: universal quantification over M

The original theorem uses `∃ M` — we get to *choose* how far to extend the range.
The most natural strengthening replaces this with `∀ M` (the density bound must hold
for *every* sufficiently large `M`, not just some).

**This variant is false.** The counterexample: take `A = {1}` (a valid Sidon set in
`[1, N]`) and `M = N + 1`. Then `B ⊆ [N + 1, N + 1] = {N + 1}`, which forces
`|A ∪ B| ≤ 2`. But `(1 − ε) √(N + 1) → ∞` as `N → ∞`, so the density bound
fails for large `N`.

This identifies `∃ M` as the critical quantifier: the freedom to *choose* how far to
extend is what makes the original statement plausible.
-/

/-- Singleton sets are Sidon. -/
lemma isSidonFinset_singleton (x : ℕ) : IsSidonFinset {x} := by
  exact fun a b c d ha hb hc hd hab => by aesop

/-- When `A = {1}` and `B ⊆ {N + 1}`, the union `A ∪ B` has at most 2 elements. -/
lemma card_union_singleton_le (A : Finset ℕ) (B : Finset ℕ)
    (hA : A = {1}) (hB : B ⊆ ({N + 1} : Finset ℕ)) :
    (A ∪ B).card ≤ 2 := by
  have h_card : B.card ≤ 1 := by
    exact Finset.card_le_card hB
  exact le_trans (Finset.card_union_le _ _) (by norm_num [hA]; linarith)

/-- For `N ≥ 16`, we have `(1/2) * √(N + 1) > 2`. -/
lemma half_sqrt_gt_two (N : ℕ) (hN : N ≥ 16) :
    (2 : ℝ) < (1 / 2 : ℝ) * Real.sqrt (↑N + 1) := by
  nlinarith [Real.sqrt_nonneg (N + 1 : ℝ),
    Real.sq_sqrt (show (0 : ℝ) ≤ N + 1 by positivity),
    (by norm_cast : (16 : ℝ) ≤ N)]

/-- The universal-M variant of Erdős 44 is **false**: changing `∃ M` to `∀ M`
(requiring the density bound for every large `M`, not just some) admits a
counterexample.

*Proof.* Instantiate `ε = 1/4`, `A = {1} ⊆ [1, N]` for `N` large, and
`M = N + 1`. Then `B ⊆ [N + 1, N + 1] = {N + 1}` forces `|A ∪ B| ≤ 2`, while
`(3/4) √(N + 1) → ∞`. -/
theorem erdos_44_universal_M_false :
    ¬(∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∀ M : ℕ, M ≥ max N Mε →
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  push_neg
  refine ⟨1 / 4, ?_, ?_⟩ <;> norm_num
  intro Mε
  refine ⟨16 + Mε ^ 2, ?_, {1}, ?_, ?_, 16 + Mε ^ 2 + 1, ?_, ?_⟩ <;> norm_num
  · nlinarith
  · nlinarith
  · exact isSidonFinset_singleton 1
  · nlinarith
  · constructor <;> intro h <;>
      nlinarith [Real.sqrt_nonneg (16 + Mε ^ 2 + 1),
        Real.sq_sqrt (show 0 ≤ 16 + (Mε : ℝ) ^ 2 + 1 by positivity)]

end Erdos44
