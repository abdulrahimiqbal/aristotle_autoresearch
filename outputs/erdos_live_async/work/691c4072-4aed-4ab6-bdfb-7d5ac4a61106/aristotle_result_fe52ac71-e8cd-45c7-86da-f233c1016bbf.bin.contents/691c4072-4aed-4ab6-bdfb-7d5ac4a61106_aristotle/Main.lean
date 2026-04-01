/-
Experiment ID: 691c4072-4aed-4ab6-bdfb-7d5ac4a61106
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 29, "target": "negated_weakening"}
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

/-- Equivalent explicit-binder formulation, amenable to `Decidable` synthesis. -/
private def IsSidonExplicit (A : Finset ℕ) : Prop :=
  ∀ a ∈ A, ∀ b ∈ A, ∀ c ∈ A, ∀ d ∈ A,
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

private theorem isSidon_equiv (A : Finset ℕ) : IsSidonFinset A ↔ IsSidonExplicit A :=
  ⟨fun h a ha b hb c hc d hd heq => @h a b c d ha hb hc hd heq,
   fun h a b c d ha hb hc hd heq => h a ha b hb c hc d hd heq⟩

instance decidableIsSidonFinset (A : Finset ℕ) : Decidable (IsSidonFinset A) := by
  rw [isSidon_equiv]; unfold IsSidonExplicit; exact inferInstance

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**Status**: This is a formalization of Erdős Problem 44, which remains an open problem
in additive combinatorics. The best known result (Cilleruelo, 2001, building on
Erdős–Turán 1941 and Lindström 1969) shows Sidon sets in [1,N] of size ∼ √N exist,
but the full extension property with (1-ε)√M density is unresolved. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

/-! ## Negated weakening and counterexample search

We consider a natural **weakening** of the Erdős conjecture above: dropping the
extension requirement and simply asking that arbitrarily large Sidon subsets of
initial intervals exist with density approaching √N.

**Weakened statement**: For all ε > 0, for all sufficiently large N, there exists a
Sidon set A ⊆ [1, N] with |A| ≥ (1 − ε) · √N.

The **negation** of this weakening asserts a *uniform density gap*: some fixed ε > 0
bounds every Sidon set in [1, N] away from √N for arbitrarily large N.

We show this negation is **false** by exhibiting explicit Sidon sets whose
density refutes any proposed gap.
-/

/-- The negated weakening: there exists ε > 0 such that for all M₀, there
exists N ≥ M₀ for which *every* Sidon subset of [1,N] has fewer than
(1 − ε) · √N elements. -/
def NegatedWeakening : Prop :=
  ∃ ε : ℝ, ε > 0 ∧
    ∀ M₀ : ℕ, ∃ N : ℕ, N ≥ M₀ ∧
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        (A.card : ℝ) < (1 - ε) * Real.sqrt (N : ℝ)

/-! ### Concrete Sidon set constructions -/

/-- {1, 2, 5, 11}: Sidon set of size 4 in [1, 11]. -/
def sidon4 : Finset ℕ := {1, 2, 5, 11}

theorem sidon4_subset : sidon4 ⊆ Finset.Icc 1 11 := by native_decide
theorem sidon4_isSidon : IsSidonFinset sidon4 := by native_decide
theorem sidon4_card : sidon4.card = 4 := by native_decide

/-- {1, 2, 4, 8, 13, 21}: Sidon set of size 6 in [1, 21]. -/
def sidon6 : Finset ℕ := {1, 2, 4, 8, 13, 21}

theorem sidon6_subset : sidon6 ⊆ Finset.Icc 1 21 := by native_decide
theorem sidon6_isSidon : IsSidonFinset sidon6 := by native_decide
theorem sidon6_card : sidon6.card = 6 := by native_decide

/-- {1, 2, 4, 8, 13, 21, 31}: Sidon set of size 7 in [1, 31].
Shift of the classic set {0, 1, 3, 7, 12, 20, 30}. -/
def sidon7 : Finset ℕ := {1, 2, 4, 8, 13, 21, 31}

theorem sidon7_subset : sidon7 ⊆ Finset.Icc 1 31 := by native_decide
theorem sidon7_isSidon : IsSidonFinset sidon7 := by native_decide
theorem sidon7_card : sidon7.card = 7 := by native_decide

/-! ### Density bounds refuting the negated weakening

| Set     | N  | |A| | √N    | |A|/√N |
|---------|-----|-----|-------|--------|
| sidon4  | 11  | 4   | 3.32  | 1.21   |
| sidon6  | 21  | 6   | 4.58  | 1.31   |
| sidon7  | 31  | 7   | 5.57  | 1.26   |

Since |A| > √N in each case, (1 − ε) · √N < |A| for all ε ∈ (0, 1].
More precisely, 6/√21 > 1.3 and 7/√31 > 1.25, so even (1 − ε) · √N < |A|
for ε as small as 0.2.
-/

/-
6 ≥ (1/2) · √21
-/
theorem sidon6_density_bound : (6 : ℝ) ≥ (1 / 2) * Real.sqrt 21 := by
  nlinarith [ Real.sq_sqrt ( show 0 ≤ 21 by norm_num ) ]

/-
7 ≥ (1/2) · √31
-/
theorem sidon7_density_bound : (7 : ℝ) ≥ (1 / 2) * Real.sqrt 31 := by
  nlinarith [ Real.sq_sqrt ( show 0 ≤ 31 by norm_num ) ]

/-
For any ε ∈ (0, 1/2], the negated weakening fails at N = 21.
-/
theorem negated_weakening_counterexample_at_21 (ε : ℝ) (hε : ε > 0) (hε1 : ε ≤ 1 / 2) :
    ∃ A : Finset ℕ, A ⊆ Finset.Icc 1 21 ∧ IsSidonFinset A ∧
      (1 - ε) * Real.sqrt 21 ≤ (A.card : ℝ) := by
  use sidon6;
  exact ⟨ by native_decide, by native_decide, by norm_num [ sidon6_card ] ; nlinarith [ Real.sqrt_nonneg 21, Real.sq_sqrt ( show 0 ≤ 21 by norm_num ) ] ⟩

/-
For any ε ∈ (0, 1/2], the negated weakening fails at N = 31.
-/
theorem negated_weakening_counterexample_at_31 (ε : ℝ) (hε : ε > 0) (hε1 : ε ≤ 1 / 2) :
    ∃ A : Finset ℕ, A ⊆ Finset.Icc 1 31 ∧ IsSidonFinset A ∧
      (1 - ε) * Real.sqrt 31 ≤ (A.card : ℝ) := by
  exact ⟨ sidon7, by native_decide, by native_decide, by push_cast [ sidon7_card ] ; nlinarith [ Real.sqrt_nonneg 31, Real.sq_sqrt ( show 0 ≤ 31 by norm_num ) ] ⟩

end Erdos44