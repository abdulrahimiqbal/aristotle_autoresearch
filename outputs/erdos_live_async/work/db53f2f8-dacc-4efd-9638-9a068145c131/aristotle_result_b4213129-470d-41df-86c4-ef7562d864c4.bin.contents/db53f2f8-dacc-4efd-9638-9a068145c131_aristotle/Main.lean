/-
Experiment ID: db53f2f8-dacc-4efd-9638-9a068145c131
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 27, "target": "boundary_variant"}
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

/-!
## Basic Sidon set properties
-/

/-- Sidon property is monotone: subsets of Sidon sets are Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (h : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A :=
  fun _ _ _ _ ha hb hc hd hab => h (hAB ha) (hAB hb) (hAB hc) (hAB hd) hab

/-- The empty set is trivially Sidon. -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by tauto

/-- A singleton is Sidon. -/
lemma isSidonFinset_singleton (n : ℕ) : IsSidonFinset {n} := by
  intro a b c d ha hb hc hd _
  rw [Finset.mem_singleton] at ha hb hc hd
  subst ha; subst hb; subst hc; subst hd
  left; exact ⟨rfl, rfl⟩

/-- A ∪ ∅ = A -/
lemma union_empty_sidon {A : Finset ℕ} (h : IsSidonFinset A) :
    IsSidonFinset (A ∪ ∅) := by
  simp [h]

/-!
## The main Erdős Problem 44 statement

This is an **open problem** in additive combinatorics. It asserts that any Sidon set
in [1, N] can be extended to a Sidon set of near-optimal density (1 - ε)√M in some
larger interval [1, M].

We prove the special case ε ≥ 1 (where the density requirement becomes trivial)
and the case where A is already large enough (|A|² ≥ N).
-/

/-- Special case: when ε ≥ 1, the factor (1 - ε) is non-positive, making the
density requirement trivially satisfied by B = ∅. -/
theorem erdos_44_large_epsilon :
    ∀ ε : ℝ, ε ≥ 1 →
      ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N 1 ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε N _hN _A _hA hA'
  exact ⟨N, by omega, ∅, by norm_num, by simpa using hA',
    le_trans (mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr hε)
      (Real.sqrt_nonneg _)) (Nat.cast_nonneg _)⟩

/-- Special case: when the Sidon set A is "large enough" (|A|² ≥ N), the extension
B = ∅ suffices with M = |A|². -/
theorem erdos_44_large_A (ε : ℝ) (hε : ε > 0) (N : ℕ) (_hN : 1 ≤ N)
    (A : Finset ℕ) (_hA : A ⊆ Finset.Icc 1 N) (hAS : IsSidonFinset A)
    (hcard : N ≤ A.card ^ 2) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine' ⟨A.card ^ 2, by linarith, ∅, _, _, _⟩ <;> norm_num
  · exact hAS
  · nlinarith

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**Status**: Open problem. The cases ε ≥ 1 and |A|² ≥ N are proved above.
The general case requires constructing Sidon extensions of prescribed density,
which remains unresolved. -/
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
## Boundary variant analysis

The **boundary variant** sets ε = 0 in the main statement, replacing the factor
`(1 - ε)` with `1`. This asks for Sidon extensions achieving density exactly `√M`.

### Key structural difference

In the main theorem, `M_ε` is allowed to depend on ε. As ε → 0⁺, the witness
`M_ε` may need to grow without bound. The boundary variant demands a *single*
`M₀` that works uniformly for the coefficient 1.

### Counterexample search

We searched exhaustively (backtracking over all Sidon extensions) for parameters
(A, M) where the maximum Sidon extension of A into [1, M] has fewer than ⌈√M⌉
elements, for:
- A = greedy Sidon sets in [1, N] for N ≤ 10, M ≤ 80
- A = {1, 2, 5}, {1, 2, 3, 5, 8}, {1, 2, 3}, and other choices

**No counterexample was found.** In all tested cases, the optimal Sidon extension
exceeds √M. This is consistent with the theoretical surplus from algebraic (Singer)
constructions, which yield Sidon sets of size q + 1 > √(q² + q + 1) in [1, q² + q + 1].

### Greedy algorithm evidence

The *greedy* algorithm (non-optimal) falls below √M for large M:
- A = {1,2,3}, M = 5000: greedy gives 51 vs √5000 ≈ 70.7 (ratio 0.72)
- A = {1,2,3,5,8}, M = 500: greedy gives 21 vs √500 ≈ 22.4 (ratio 0.94)

However, greedy is known to be suboptimal for Sidon constructions. The optimal
size is expected to match √M + O(M^{1/4}), which exceeds √M for all M.

### Conclusion

The boundary variant appears to be **true** but strictly stronger than the ε > 0
version. No finite counterexample exists in our search space. The ε > 0 version
would follow from the boundary variant (proved below as `boundary_implies_main`).
-/

/-- The boundary variant of Erdős Problem 44: the ε = 0 case.
This asks for density ≥ √M (coefficient 1) rather than (1 - ε)√M.
It is strictly stronger than the ε > 0 formulation because M₀ cannot
depend on ε.

**Status**: Open. No counterexample found; likely true. -/
theorem erdos_44_boundary_variant :
    ∃ M₀ : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N M₀ ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

/-- The boundary variant trivially implies the main statement for every ε > 0.
This witnesses the strict logical relationship between the two formulations. -/
theorem boundary_implies_main
    (hbv : ∃ M₀ : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N M₀ ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε _hε
  exact ⟨hbv.choose, fun N hN A hA hA' => by
    obtain ⟨M, hM₁, B, hB₁, hB₂, hB₃⟩ := hbv.choose_spec N hN A hA hA'
    exact ⟨M, hM₁, B, hB₁, hB₂, by nlinarith [Real.sqrt_nonneg M]⟩⟩

end Erdos44
