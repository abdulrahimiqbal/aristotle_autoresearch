/-
Experiment ID: 7cc167fe-1c25-48e4-839b-2bed3ee43638
Move: reformulate
Move family: equivalent_view
Theorem family: erdos_problem
Phase: consolidation
Modification: {"form": "a positive solution to Erdos problem 707 would imply this problem"}
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

/-- The empty set is Sidon. -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  intro a b c d ha
  simp at ha

/-- Any subset of a Sidon set is Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (hB : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A := by
  intro a b c d ha hb hc hd he
  exact hB (hAB ha) (hAB hb) (hAB hc) (hAB hd) he

/-
PROBLEM
For ε ≥ 1, the statement is trivially true: (1-ε)√M ≤ 0 ≤ |A ∪ B|.

PROVIDED SOLUTION
For ε ≥ 1, (1-ε) ≤ 0. Choose Mε = 1. Given N ≥ 1 and Sidon A ⊆ {1,...,N}, choose M = max N 1 = N and B = ∅. Then:
- M ≥ max N Mε ✓ (M = N ≥ N and N ≥ 1 = Mε)
- B = ∅ ⊆ Finset.Icc (N+1) M ✓
- A ∪ ∅ = A is Sidon ✓ (given)
- (1-ε)√M ≤ 0 ≤ |A| = |A ∪ ∅| ✓ (since 1-ε ≤ 0 and √M ≥ 0, so (1-ε)√M ≤ 0, and |A| ≥ 0 as a natural number cast to ℝ)

Key lemmas: Finset.union_empty, mul_nonpos_of_nonpos_of_nonneg, Real.sqrt_nonneg, Nat.cast_nonneg
-/
lemma erdos_44_easy (ε : ℝ) (_hε : ε > 0) (hε1 : ε ≥ 1) :
    ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N Mε ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  use 1;
  intro N hN A hA hSidon
  use N
  simp [hN];
  exact ⟨ hSidon, le_trans ( mul_nonpos_of_nonpos_of_nonneg ( sub_nonpos_of_le hε1 ) ( Real.sqrt_nonneg _ ) ) ( Nat.cast_nonneg _ ) ⟩

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**STATUS**: This is an OPEN PROBLEM in additive combinatorics. It is essentially equivalent
to Erdős Problem 707 (existence of near-optimal Sidon sets). See Analysis.md for a detailed
analysis of the mathematical content, proof obstacles, and the relationship between this
reformulation and the original problem.

The reformulation is neither easier nor harder than Erdős 707:
- Even the case A = ∅ requires constructing Sidon sets of near-optimal density
- The freedom to choose M does not help because the density requirement scales with √M
- Known constructions (Singer, Erdős-Turán) achieve density at most 1/√2 ≈ 0.707
  when conflicts with A must be avoided, insufficient for ε < 0.293
-/
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