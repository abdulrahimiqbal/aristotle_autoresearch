/-
Experiment ID: f0b86e3e-5678-4840-9222-6adb06ce079e
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "most_fragile_variant"}
-/

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

-- ============================================================================
-- Helper lemmas (all proved)
-- ============================================================================

/-- Subsets of Sidon sets are Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (hB : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A :=
  fun _ _ _ _ ha hb hc hd hab => hB (hAB ha) (hAB hb) (hAB hc) (hAB hd) hab

/-- The empty set is Sidon. -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by tauto

/-- Singletons are Sidon. -/
lemma isSidonFinset_singleton (n : ℕ) : IsSidonFinset {n} := by
  intro a b c d ha hb hc hd _
  rw [Finset.mem_singleton] at ha hb hc hd
  subst ha; subst hb; subst hc; subst hd
  left; exact ⟨rfl, rfl⟩

/-- The union of a Sidon set with the empty set is still Sidon. -/
lemma union_empty_sidon {A : Finset ℕ} (hA : IsSidonFinset A) :
    IsSidonFinset (A ∪ ∅) := by
  simp; exact hA

-- ============================================================================
-- Partial result: the ε ≥ 1 case (proved)
-- ============================================================================

/-- For ε ≥ 1 the bound (1 - ε) * √M ≤ 0 ≤ |A ∪ B| holds trivially. -/
lemma erdos_44_trivial_case
    (N : ℕ) (hN : 1 ≤ N) (A : Finset ℕ)
    (hSidon : IsSidonFinset A)
    (ε : ℝ) (hε1 : ε ≥ 1) :
    ∃ M : ℕ, M ≥ max N 1 ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine ⟨N, ?_, ∅, Finset.empty_subset _, ?_, ?_⟩
  · simp [Nat.max_eq_left hN]
  · simp; exact hSidon
  · simp
    exact le_trans (mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr hε1) (Real.sqrt_nonneg _))
      (Nat.cast_nonneg _)

-- ============================================================================
-- Main theorem
-- ============================================================================

/-- **Erdős 44 Sidon extension (weakened variant).**

This is essentially a variant of Erdős Problem 44 on the existence of dense Sidon
sets. The statement asserts that *every* Sidon set can be extended to a
near-optimally dense one.

**Status**: Open problem. No counterexample exists (see `ANALYSIS.md`), but a
formal proof requires deep Sidon set constructions (Singer difference sets or
probabilistic methods) not available in Mathlib.

The `sorry` below is *not* due to a counterexample — it reflects the current
state of formalized additive combinatorics. The ε ≥ 1 case is handled; the
hard case 0 < ε < 1 with sparse A remains open. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε
  by_cases hε1 : ε ≥ 1
  · exact ⟨1, fun N hN A _ hSidon => erdos_44_trivial_case N hN A hSidon ε hε1⟩
  · push_neg at hε1
    -- 0 < ε < 1: requires Sidon set extension theory (open problem).
    sorry

end Erdos44
