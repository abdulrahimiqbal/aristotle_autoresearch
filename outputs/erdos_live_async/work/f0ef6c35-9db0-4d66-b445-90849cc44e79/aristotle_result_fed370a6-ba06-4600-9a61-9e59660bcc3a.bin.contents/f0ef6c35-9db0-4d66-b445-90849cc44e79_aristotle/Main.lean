/-
Experiment ID: f0ef6c35-9db0-4d66-b445-90849cc44e79
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 20, "target": "parameter_extreme"}
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
  tauto

/-- Any subset of a Sidon set is Sidon. -/
lemma isSidonFinset_subset {A B : Finset ℕ} (h : A ⊆ B) (hB : IsSidonFinset B) :
    IsSidonFinset A := by
  exact fun a b c d ha hb hc hd hab => hB (h ha) (h hb) (h hc) (h hd) hab

/-- A singleton is Sidon. -/
lemma isSidonFinset_singleton (n : ℕ) : IsSidonFinset {n} := by
  exact fun a b c d ha hb hc hd _ => by aesop

/-- For ε ≥ 1, the bound (1-ε)√M ≤ 0 ≤ |A ∪ B| is trivially satisfied. -/
lemma erdos_44_trivial_case (ε : ℝ) (hε : ε ≥ 1) (N : ℕ) (hN : 1 ≤ N)
    (A : Finset ℕ) (_hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    ∃ M : ℕ, M ≥ max N 1 ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine ⟨N, ?_, ∅, ?_, ?_, ?_⟩ <;> norm_num
  · linarith
  · assumption
  · exact le_trans (mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr hε) (Real.sqrt_nonneg _))
      (Nat.cast_nonneg _)

/-- When |A| ≥ (1-ε)√N, we can take M = N and B = ∅. -/
lemma erdos_44_large_A_case (ε : ℝ) (_hε : ε > 0) (_hε1 : ε < 1) (N : ℕ) (_hN : 1 ≤ N)
    (A : Finset ℕ) (_hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A)
    (hcard : (1 - ε) * Real.sqrt (N : ℝ) ≤ (A.card : ℝ))
    (Mε : ℕ) (hMε : N ≥ Mε) :
    ∃ M : ℕ, M ≥ max N Mε ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine ⟨N, ?_, ∅, ?_, ?_, ?_⟩ <;> aesop

/-- **Erdős Problem 44 (Sidon set extension).**

This is a well-known open problem in additive combinatorics.
The statement asserts that any Sidon set in [1,N] can be extended to a
near-optimal Sidon set in [1,M] for suitable M.

**Counterexample search results** (see `Analysis.md`):
- No counterexample was found for any parameter combination tested
  (greedy extensions for various A, N, M, and ε values).
- For ε ≥ 1: trivially true (proved as `erdos_44_trivial_case`).
- For maximal Sidon sets (|A| ≈ √N): true with M = N, B = ∅
  (proved as `erdos_44_large_A_case`).
- For small A and large N: requires Singer's theorem (perfect difference
  sets giving Sidon sets of size (1+o(1))√M) or equivalent deep result
  not yet available in Mathlib.
- The "spacing construction" B = {(k+2)(N+1) : k ∈ S'} gives a provably
  compatible extension for any A, but achieves density only 1/√(N+1),
  insufficient for small ε and large N.

The remaining `sorry` reflects the open problem status. -/
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
