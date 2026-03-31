/-
Experiment ID: 1e4da405-fe7a-4e26-a3b6-a04e0c4bcbb4
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 19, "target": "negated_weakening"}
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

**Status**: This is a famous open problem in additive combinatorics (Erdős Problem 44).
No formal proof is known. -/
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
## Negated weakening

The **negated weakening** strengthens the original conjecture by dropping the `(1 - ε)`
factor and requiring the bound `|A ∪ B| ≥ √M` to hold for *all* `M ≥ N` (rather than
existentially choosing a favorable `M`).

### Counterexample

Take `N = 4`, `A = {1}` (trivially Sidon in `[1, 4]`), `M = 4`.
Then `B ⊆ [5, 4] = ∅`, so the only option is `B = ∅` and
`|A ∪ B| = |{1}| = 1 < 2 = √4`.

This witnesses a concrete failure of the strengthened statement.
-/

/-- The singleton `{1}` is a Sidon set. -/
lemma isSidon_singleton_one : IsSidonFinset {1} := by
  exact fun a b c d ha hb hc hd hab => by aesop

/-- `{1} ⊆ Finset.Icc 1 4`. -/
lemma singleton_one_subset_Icc : ({1} : Finset ℕ) ⊆ Finset.Icc 1 4 := by
  decide +revert

/-- No subset of an empty interval is nonempty. -/
lemma Icc_empty_of_lt {a b : ℕ} (h : b < a) : Finset.Icc a b = ∅ := by
  exact Finset.Icc_eq_empty_of_lt h

/-- Key numerical fact: `√4 > 1`. -/
lemma sqrt_four_gt_one : (1 : ℝ) < Real.sqrt 4 := by
  norm_num [Real.lt_sqrt]

/-- Negated weakening: the negation of the strengthened Erdős 44 conjecture (with the
    `(1-ε)` factor removed and `∀ M ≥ N` instead of `∃ M`).

    **Counterexample**: `N = 4`, `A = {1}`, `M = 4`.  Then `B ⊆ [5, 4] = ∅`, forcing
    `B = ∅` and `|A ∪ B| = 1 < √4 = 2`. -/
theorem negated_weakening :
    ¬ (∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∀ M : ℕ, M ≥ N →
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  simp
  use 4
  constructor
  · norm_num
  · refine ⟨{1}, ?_, ?_, 4, ?_, ?_⟩ <;> norm_num
    exact fun a b c d ha hb hc hd h => by aesop

end Erdos44
