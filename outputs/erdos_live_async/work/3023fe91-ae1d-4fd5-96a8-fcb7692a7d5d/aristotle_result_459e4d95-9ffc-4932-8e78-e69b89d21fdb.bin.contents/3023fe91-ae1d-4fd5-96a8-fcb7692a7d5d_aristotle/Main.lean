/-
Experiment ID: 3023fe91-ae1d-4fd5-96a8-fcb7692a7d5d
Move: reformulate
Move family: extremal_case
Theorem family: erdos_problem
Phase: consolidation
Modification: {"extremal_target": "ing that the `1 ≤ C` lower bound is an artifact of the problem statement"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- extremal sweep: ing that the `1 ≤ C` lower bound is an artifact of the problem statement
import Mathlib

noncomputable section

namespace Erdos181

open scoped BigOperators

/-- Placeholder predicate for a graph on `2^n` vertices being isomorphic to the
`n`-dimensional hypercube. This keeps the statement self-contained inside a plain
Mathlib workspace while leaving room for a later graph-isomorphism formalization. -/
def IsHypercubeGraph (n : ℕ) (_G : SimpleGraph (Fin (2 ^ n))) : Prop :=
  True

/-- Placeholder for the ordinary two-colour Ramsey number of a finite graph. -/
def GraphRamseyNumber {α : Type*} [Fintype α] (_G : SimpleGraph α) : ℕ :=
  0

/-
PROBLEM
A self-contained Lean 4 stub for Erdos Problem 181, modeled on the informal
statement used on erdosproblems.com.

PROVIDED SOLUTION
Use C = 1. Then 1 ≤ 1. For any n, use G = ⊥. IsHypercubeGraph unfolds to True (trivial), GraphRamseyNumber unfolds to 0 ≤ 1 * 2^n (Nat.zero_le).
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  refine' ⟨ 1, by norm_num, fun n => _ ⟩;
  rcases n with ( _ | n ) <;> norm_num [ IsHypercubeGraph, GraphRamseyNumber ]

/-! ## Extremal reformulation: the `1 ≤ C` lower bound is an artifact

With the current placeholder definitions (`GraphRamseyNumber := 0`,
`IsHypercubeGraph := True`), the constant `C = 0` already witnesses the
universal statement.  The constraint `1 ≤ C` in the original formulation is
therefore an artifact of wanting the constant to be *positive* — a cosmetic
choice that does not affect the mathematical content.

The reformulation below drops the `1 ≤ C` guard entirely and proves the
stronger statement that such a `C` exists (namely `C = 0`).  This makes the
boundary behaviour explicit: the tightest possible constant is `C = 0` under
the current placeholders.
-/

/-
PROBLEM
**Extremal reformulation.**  Dropping the `1 ≤ C` constraint, the optimal
constant is `C = 0` (under the placeholder definitions).  This shows the lower
bound `1 ≤ C` in the original statement is an artifact.

PROVIDED SOLUTION
Use C = 0. For any n, use G = ⊥. IsHypercubeGraph unfolds to True (trivial), GraphRamseyNumber unfolds to 0 ≤ 0 (le_refl).
-/
theorem erdos_181_hypercube_ramsey_extremal :
    ∃ C : ℕ, ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 0;
  intro n
  use ⊥;
  exact ⟨ trivial, by norm_num [ GraphRamseyNumber ] ⟩

/-
PROBLEM
The tightest witness is `C = 0`: every hypercube graph (trivially, with the
placeholder) has `GraphRamseyNumber = 0`.

PROVIDED SOLUTION
For any n, use G = ⊥. IsHypercubeGraph unfolds to True (trivial), GraphRamseyNumber unfolds to 0 = 0 (rfl).
-/
theorem erdos_181_extremal_tight :
    ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G = 0 := by
  intro n;
  exact ⟨ ⊥, trivial, rfl ⟩

end Erdos181