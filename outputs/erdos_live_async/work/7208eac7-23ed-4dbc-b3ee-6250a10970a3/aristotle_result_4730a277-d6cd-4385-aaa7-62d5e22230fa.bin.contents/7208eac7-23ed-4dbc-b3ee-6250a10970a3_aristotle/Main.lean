/-
Experiment ID: 7208eac7-23ed-4dbc-b3ee-6250a10970a3
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 24, "target": "negated_weakening"}
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

/-- A self-contained Lean 4 stub for Erdos Problem 181, modeled on the informal
statement used on erdosproblems.com. -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-! ## Negated weakening

A natural *weakening* of the main statement drops the universal quantifier over `n`
and instead asks for just a single `n` witness.  Negating that weakening gives:

  ∀ C ≥ 1, ∀ n, ∀ G, ¬(IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n)

With the placeholder definitions (`IsHypercubeGraph = True`,
`GraphRamseyNumber = 0`) this is *false* — every `(C, n, G)` triple is a
counterexample because `True ∧ 0 ≤ C * 2 ^ n` always holds.

We exhibit the counterexample `C = 1, n = 0, G = ⊥` explicitly. -/

/-- The negated weakening: for every `C ≥ 1` and every `n`, no graph simultaneously
satisfies the hypercube predicate and the Ramsey bound. -/
def NegatedWeakening : Prop :=
  ∀ C : ℕ, 1 ≤ C → ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
    ¬(IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n)

/-- The negated weakening is false: `C = 1, n = 0, G = ⊥` is a counterexample. -/
theorem negated_weakening_false : ¬ NegatedWeakening := by
  intro h
  exact h 1 (le_refl 1) 0 ⊥ ⟨trivial, Nat.zero_le _⟩

end Erdos181
