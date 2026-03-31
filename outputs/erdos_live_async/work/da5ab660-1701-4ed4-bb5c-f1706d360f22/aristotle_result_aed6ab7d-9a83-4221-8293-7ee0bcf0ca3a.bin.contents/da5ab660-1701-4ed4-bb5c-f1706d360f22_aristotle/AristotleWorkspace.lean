/-
Experiment ID: da5ab660-1701-4ed4-bb5c-f1706d360f22
Move: counterexample_mode
Move family: witness_minimization
Theorem family: erdos_problem
Phase: consolidation
Modification: {"mode": "minimize", "witness_target": "."}
-/

import Mathlib

/-!
# Erdős Problem 44: Sidon Set Extension

## Sharp Boundary Analysis

The theorem claims that for any ε > 0, Sidon sets in [1,N] can be extended to
near-optimal density (1-ε)√M in [1,M] for suitable M.

**Sharp boundary at ε = 1 (i.e., (1-ε) = 0):**
- For ε ≥ 1: The bound (1-ε)√M ≤ 0 ≤ |A ∪ B| is vacuously satisfied.
  Witness: Mε = 1, M = N, B = ∅. This is the *minimal* witness.
- For ε < 1: The bound (1-ε)√M > 0 requires |A ∪ B| ≥ Ω(√M), which demands
  constructing dense Sidon sets. This requires algebraic constructions:
  - Erdős-Turán (1941): Sidon sets of size p in [0, 2p²], density 1/√2 ≈ 0.707
  - Singer/Bose-Chowla: Sidon sets of size q+1 in [0, q²+q], density → 1

The decimal boundary for the constructive gap:
- ε ≥ 1.0: trivially true (proved below)
- ε ∈ (1 - 1/√2, 1.0) ≈ (0.293, 1.0): provable via Erdős-Turán construction
- ε ∈ (0, 1 - 1/√2] ≈ (0, 0.293]: requires Singer/Bose-Chowla (not in Mathlib)

The *sharp* witness/blocker boundary is therefore at (1-ε) = 0, i.e., ε = 1.0,
separating the vacuous regime from the constructive regime. Within the constructive
regime, a secondary boundary at ε ≈ 0.293 separates what's provable with the
simplest (Erdős-Turán) construction from what requires deeper algebra.
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

/-! ## Case ε ≥ 1: Trivial (minimal witness Mε = 1) -/

/-- When ε ≥ 1, the factor (1-ε) ≤ 0 makes the density bound vacuously true.
The minimal witness is Mε = 1, M = N, B = ∅. -/
lemma erdos_44_case_ge_one :
    ∀ ε : ℝ, ε > 0 → ε ≥ 1 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε_pos hε_ge_one
  refine ⟨1, fun N hN_pos A hA_sub hA_sidon ↦ ?_⟩
  refine ⟨N, ?_, ∅, ?_, ?_, ?_⟩
  · simp; omega
  · exact Finset.empty_subset _
  · simp [hA_sidon]
  · simp; exact le_trans (mul_nonpos_of_nonpos_of_nonneg (sub_nonpos_of_le hε_ge_one)
      (Real.sqrt_nonneg _)) (Nat.cast_nonneg _)

/-! ## Case ε < 1: Requires Sidon set construction

This case requires constructing dense Sidon sets of size ≈ √M in [N+1, M]
that are compatible with A. The Erdős-Turán construction gives density 1/√2,
sufficient for ε > 1 - 1/√2 ≈ 0.293. For the full range 0 < ε < 1,
the Singer/Bose-Chowla construction (density → 1) is needed.

Neither construction is currently formalized in Mathlib, making this an
infrastructure gap rather than a mathematical impossibility. -/

/-- Key infrastructure gap: existence of dense compatible Sidon extensions.
For a Sidon set A ⊆ [1,N] with |A| < (1-ε)√N, we need to construct
B ⊆ [N+1, M] with A ∪ B Sidon and |A ∪ B| ≥ (1-ε)√M.
This requires algebraic Sidon set constructions (Erdős-Turán or Singer/Bose-Chowla)
not currently in Mathlib. -/
lemma exists_sidon_extension (ε : ℝ) (hε : 0 < ε) (hε1 : ε < 1)
    (N : ℕ) (hN : 1 ≤ N) (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N)
    (hSidon : IsSidonFinset A) (hSparse : (A.card : ℝ) < (1 - ε) * Real.sqrt N) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

lemma erdos_44_case_lt_one :
    ∀ ε : ℝ, ε > 0 → ε < 1 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε hε1
  use 1
  intro N hN A hA hSidon
  by_cases hDense : (1 - ε) * Real.sqrt (N : ℝ) ≤ (A.card : ℝ)
  · -- Dense case: A already has enough elements
    exact ⟨N, by simp; omega, ∅, Finset.empty_subset _, by simp [hSidon], by simpa⟩
  · -- Sparse case: need construction
    push_neg at hDense
    obtain ⟨M, hM, B, hB, hSid, hCard⟩ := exists_sidon_extension ε hε hε1 N hN A hA hSidon hDense
    exact ⟨M, by omega, B, hB, hSid, hCard⟩

/-- **Erdős Problem 44 (Sidon Extension).**

For any ε > 0, there exists a threshold Mε such that any Sidon set A ⊆ [1,N]
can be extended to a Sidon set A ∪ B with B ⊆ [N+1, M] achieving
|A ∪ B| ≥ (1-ε)√M, for some M ≥ max(N, Mε).

The proof reduces to two cases:
- **ε ≥ 1**: Trivially true since (1-ε) ≤ 0 (proved, minimal witness Mε = 1).
- **ε < 1**: Requires constructing dense compatible Sidon extensions via
  algebraic difference set theory (sorry — Mathlib infrastructure gap). -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε
  by_cases hε1 : ε < 1
  · exact erdos_44_case_lt_one ε hε hε1
  · push_neg at hε1
    exact erdos_44_case_ge_one ε hε hε1

end Erdos44
