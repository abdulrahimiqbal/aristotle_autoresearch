/-
Experiment ID: f1c34b98-79e1-406d-bb05-c2b65677544f
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
With the placeholder definitions, IsHypercubeGraph n G = True and GraphRamseyNumber G = 0. So we need ∃ C, 1 ≤ C ∧ ∀ n, ∃ G, True ∧ 0 ≤ C * 2^n. Take C = 1, use any graph (e.g. ⊥), and the bound is trivial since 0 ≤ 1 * 2^n. Unfold IsHypercubeGraph and GraphRamseyNumber to reduce to trivial goals.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Let's choose $C$ to be 1.
  use 1
  simp [IsHypercubeGraph, GraphRamseyNumber]

/-
PROBLEM
**Boundary variant (lower bound)**: Does the hypercube Ramsey number grow at
least linearly in `2^n`?  That is, does there exist a positive constant `c` such
that for every `n` and every hypercube graph `G` on `2^n` vertices,
`GraphRamseyNumber G ≥ c * 2^n`?

With the current placeholder definitions (`GraphRamseyNumber := 0`), this is
*false*: no positive constant can lower-bound 0.  We exhibit a formal
counterexample below.

PROVIDED SOLUTION
Unfold GraphRamseyNumber to 0 and IsHypercubeGraph to True. Then the statement becomes ¬(∃ c, 1 ≤ c ∧ ∀ n, ∀ G, True → c * 2^n ≤ 0). Push the negation in. Given c ≥ 1, specialize at n = 1 and any graph to get c * 2 ≤ 0, which contradicts c ≥ 1. Use omega or positivity.
-/
theorem boundary_variant_lower_bound_false :
    ¬ (∃ c : ℕ, 1 ≤ c ∧ ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → c * 2 ^ n ≤ GraphRamseyNumber G) := by
  simp +zetaDelta at *;
  exact fun n hn => ⟨ 0, ⊥, by unfold IsHypercubeGraph; aesop, by unfold GraphRamseyNumber; aesop ⟩

end Erdos181