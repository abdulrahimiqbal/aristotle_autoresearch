/-
Experiment ID: 05c0efe9-8fee-4f1e-b379-9d461b4d9028
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 26, "target": "most_fragile_variant"}
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
With the placeholder definitions, IsHypercubeGraph n G = True and GraphRamseyNumber G = 0. So we need ∃ C ≥ 1, ∀ n, ∃ G, True ∧ 0 ≤ C * 2^n. Use C = 1. For each n, pick G = ⊥ (the empty graph). Unfold IsHypercubeGraph and GraphRamseyNumber, then everything reduces to trivial goals.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 1;
  simp [IsHypercubeGraph, GraphRamseyNumber]

/-
PROBLEM
**Most fragile variant (lower bound).**
The natural strengthening of Erdős 181 would be a *matching* lower bound
`r(Qₙ) ≥ c · 2ⁿ` for some constant `c > 0`. With the placeholder
`GraphRamseyNumber := 0`, this is **false** for `n ≥ 1`: the Ramsey number
is identically zero, so no linear lower bound can hold.

We formalize a counterexample: there is NO positive constant `c` such that
`c * 2^n ≤ GraphRamseyNumber G` for every `n` and every hypercube graph `G`.

PROVIDED SOLUTION
Unfold GraphRamseyNumber (which is 0) and IsHypercubeGraph (which is True). Intro the hypothesis ⟨c, hc, h⟩. Specialize h at n = 0 (or n = 1) with G = ⊥. Since IsHypercubeGraph is True, the hypothesis gives c * 2^n ≤ 0 which contradicts 1 ≤ c and positivity of 2^n. Use omega or Nat.not_succ_le_zero after simplification.
-/
theorem fragile_variant_lower_bound_false :
    ¬ (∃ c : ℕ, 1 ≤ c ∧ ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → c * 2 ^ n ≤ GraphRamseyNumber G) := by
  unfold GraphRamseyNumber IsHypercubeGraph; aesop;

end Erdos181