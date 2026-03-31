/-
Experiment ID: 0cb7da44-3cfd-460f-a423-0e6d96f44a88
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 40, "target": "parameter_extreme"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
import Mathlib

noncomputable section

namespace Erdos181

open scoped BigOperators

/-- Placeholder predicate for a graph on `2^n` vertices being isomorphic to the
`n`-dimensional hypercube. This keeps the statement self-contained inside a plain
Mathlib workspace while leaving room for a later graph-isomorphism formalization. -/
def IsHypercubeGraph (n : ℕ) (G : SimpleGraph (Fin (2 ^ n))) : Prop :=
  True

/-- Placeholder for the ordinary two-colour Ramsey number of a finite graph. -/
def GraphRamseyNumber {α : Type*} [Fintype α] (G : SimpleGraph α) : ℕ :=
  0

/-
PROBLEM
A self-contained Lean 4 stub for Erdos Problem 181, modeled on the informal
statement used on erdosproblems.com.

PROVIDED SOLUTION
With the placeholder definitions, IsHypercubeGraph is True and GraphRamseyNumber is 0. So we need: ∃ C, 1 ≤ C ∧ ∀ n, ∃ G, True ∧ 0 ≤ C * 2^n. Use C = 1, any G (e.g. ⊥ i.e. the empty graph), True is trivial, and 0 ≤ anything for Nat.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Choose C = 1
  use 1
  simp;
  intro n
  use ⊥;
  exact ⟨ trivial, Nat.zero_le _ ⟩

/-
PROBLEM
**Parameter-extreme analysis**: The constraint `1 ≤ C` is *not tight* with the
current placeholder definitions. Even `C = 0` satisfies the inner quantifier,
showing that the `1 ≤ C` lower bound is an artifact of the problem statement
rather than being forced by the mathematical content of the placeholders.

This serves as an independence witness: the bound `GraphRamseyNumber G ≤ C * 2^n`
is satisfiable at the parameter extreme `C = 0` because `GraphRamseyNumber` is
defined to be `0`.

PROVIDED SOLUTION
GraphRamseyNumber is 0 and IsHypercubeGraph is True. Use ⊥ as the graph. Then 0 ≤ 0 * 2^n simplifies to 0 ≤ 0.
-/
theorem parameter_extreme_C_eq_zero :
    ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ 0 * 2 ^ n := by
  norm_num +zetaDelta at *;
  intro n
  use ⊥;
  exact ⟨ trivial, rfl ⟩

/-
PROBLEM
Conversely, if we *negate* the original statement by requiring `C = 0` and
`1 ≤ C` simultaneously, we get a contradiction — confirming that `C = 0` is
excluded only by the explicit `1 ≤ C` guard, not by the Ramsey bound itself.

PROVIDED SOLUTION
¬ (1 ≤ 0) for Nat is trivially true by omega.
-/
theorem parameter_extreme_guard_necessary :
    ¬ (1 ≤ (0 : ℕ)) := by
  norm_num

end Erdos181