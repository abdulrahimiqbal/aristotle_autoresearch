/-
Experiment ID: 6c666bdf-6af9-4af5-9646-2689380b4a73
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "negated_weakening", "attempt": 19}
-/

-- counterexample mode target
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
With the placeholder definitions, IsHypercubeGraph n G = True and GraphRamseyNumber G = 0. So we need ∃ C, 1 ≤ C ∧ ∀ n, ∃ G, True ∧ 0 ≤ C * 2^n. Take C = 1. For any n, take G = ⊥ (the empty graph). Unfold IsHypercubeGraph to True, unfold GraphRamseyNumber to 0. Everything follows by trivial/positivity.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Set $C$ to be $1$.
  use 1
  simp_all +decide [Erdos181.IsHypercubeGraph, Erdos181.GraphRamseyNumber]

/-- **Negated weakening**: The negation of a weakened form of the theorem, which
drops the `1 ≤ C` requirement and the `IsHypercubeGraph` condition.
With the placeholder definitions (`GraphRamseyNumber = 0`), the weakened
statement is trivially true, so its negation is *false*.
We prove it is false by providing C = 0 as a counterexample. -/
theorem negated_weakening_is_false :
    ¬ (¬ ∃ C : ℕ, ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      GraphRamseyNumber G ≤ C * 2 ^ n) := by
  push_neg
  exact ⟨0, fun n => ⟨⊥, by simp [GraphRamseyNumber]⟩⟩

/-- The negated weakening statement itself. We show it is *disprovable*:
there IS a constant `C` such that for every `n` a graph with small Ramsey
number exists (in fact `GraphRamseyNumber = 0` for every graph by definition).
Hence the negation is false, and `C = 0` is the explicit counterexample
witnessing this. -/
theorem negated_weakening_counterexample :
    ∃ C : ℕ, ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      GraphRamseyNumber G ≤ C * 2 ^ n :=
  ⟨0, fun n => ⟨⊥, by simp [GraphRamseyNumber]⟩⟩

end Erdos181