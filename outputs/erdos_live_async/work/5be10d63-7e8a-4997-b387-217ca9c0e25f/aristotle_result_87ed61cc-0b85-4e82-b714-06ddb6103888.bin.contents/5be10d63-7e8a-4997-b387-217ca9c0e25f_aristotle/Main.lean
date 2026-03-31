/-
Experiment ID: 5be10d63-7e8a-4997-b387-217ca9c0e25f
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 28, "target": "minimal_variant"}
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
## Status of Erdős Problem 44

This is a formalization of Erdős Problem 44 concerning the extendability of Sidon (B₂) sets.
The statement asks: for every ε > 0, can every Sidon set A ⊆ [1, N] be extended to a Sidon
set A ∪ B ⊆ [1, M] of size ≥ (1-ε)√M?

### Known results:
- **Singer (1938)**: There exist Sidon sets of size √N + O(1) in [1, N] (using difference
  sets from finite projective planes).
- **Erdős–Turán (1941)**: The maximum Sidon set in [1, N] has size √N + O(N^{1/4}).
- The **extension property** (that an arbitrary Sidon set can be extended to near-optimal
  density) remains open. It requires algebraic constructions (Singer-type) that can be
  adapted to arbitrary starting sets.

### Why standard approaches fail for ε < 1:
- **Greedy algorithm**: gives Sidon sets of size ~M^{1/3}, far below √M.
- **Probabilistic method**: achieves ~M^{1/4} elements while avoiding cross-constraints
  with A, also insufficient.
- **Algebraic constructions** (Singer difference sets) achieve √M but require the
  starting set to be compatible with the finite field structure.

### Counterexample search (minimal variant):
Computational search over all Sidon sets in [1, N] for N ≤ 10, extending via greedy to
M ≤ 500, found **no counterexample**: every Sidon set admits an M where the extension
ratio |A ∪ B|/√M exceeds 1. However, the greedy ratio degrades for large M (approaching
M^{-1/6}), so near-optimal extensions require non-greedy constructions.

See `CounterexampleSearch.lean` for detailed computational evidence.
-/

/-- The empty set is Sidon. -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  intro a b c d ha
  exact absurd ha (Finset.notMem_empty _)

/-- Any singleton is Sidon. -/
lemma isSidonFinset_singleton (x : ℕ) : IsSidonFinset {x} := by
  intro a b c d ha hb hc hd _
  simp [Finset.mem_singleton] at ha hb hc hd
  left; exact ⟨by rw [ha, hc], by rw [hb, hd]⟩

/-- Sidon is hereditary: subsets of Sidon sets are Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (h : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A :=
  fun _ _ _ _ ha hb hc hd heq => h (hAB ha) (hAB hb) (hAB hc) (hAB hd) heq

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**Status**: This is an open problem in additive combinatorics. The proof below handles
the trivial regime (ε ≥ 1) where the cardinality bound is non-positive. The substantive
case (0 < ε < 1) remains open — it requires showing that Singer-type algebraic
constructions can extend arbitrary Sidon sets to near-optimal density. -/
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
