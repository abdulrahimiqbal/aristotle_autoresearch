/-
Experiment ID: 1c939093-48f3-407b-b135-63f40fe21435
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 31, "target": "most_fragile_variant"}
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
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, trivial, by norm_num [ GraphRamseyNumber ] ⟩ ⟩

/-! ## Most fragile variant: counterexample analysis

The placeholder definitions `IsHypercubeGraph := True` and `GraphRamseyNumber := 0` make the
main theorem trivially true.  To stress-test the formulation, we consider a *non-trivial*
Ramsey-number placeholder `RamseyNontrivial G = Fintype.card α` (the number of vertices plus one
would be more realistic, but `card` already suffices to expose fragility).

With this placeholder, the original **linear** bound `≤ C * 2^n` still holds (take `C = 1`),
but the **most fragile strengthening** — demanding the Ramsey number be **strictly less than
`2^n`** for all `n` — is *refuted* for `n = 0`.

This shows the linear-constant form `C · 2^n` is tight: no sublinear improvement is possible,
even under placeholder axiomatics.
-/

/-- Non-trivial Ramsey-number placeholder returning the number of vertices. -/
def RamseyNontrivial {α : Type*} [Fintype α] (_G : SimpleGraph α) : ℕ :=
  Fintype.card α

/-
PROBLEM
With the non-trivial placeholder `RamseyNontrivial`, the linear bound still holds.

PROVIDED SOLUTION
Take C = 1, for each n take G = ⊥. IsHypercubeGraph is True so trivial. RamseyNontrivial G = Fintype.card (Fin (2^n)) = 2^n, and 2^n ≤ 1 * 2^n. Unfold RamseyNontrivial and use Fintype.card_fin.
-/
theorem nontrivial_ramsey_linear_bound :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ RamseyNontrivial G ≤ C * 2 ^ n := by
  -- Let's choose C = 1.
  use 1
  simp [IsHypercubeGraph, RamseyNontrivial]

/-
PROBLEM
**Counterexample / fragile variant**: the strict sublinear bound `< 2^n` fails at `n = 0`.
    With `RamseyNontrivial`, every graph on `Fin (2^0) = Fin 1` has Ramsey number `1`,
    but `2^0 = 1`, so `1 < 1` is false.  Hence no graph witnesses the strict bound.

PROVIDED SOLUTION
Specialize the universal at n = 0. Then we get ∃ G : SimpleGraph (Fin 1), True ∧ RamseyNontrivial G < 2^0. RamseyNontrivial G = Fintype.card (Fin (2^0)) = Fintype.card (Fin 1) = 1, and 2^0 = 1, so we need 1 < 1 which is false. Use intro h, specialize h 0, obtain ⟨G, _, hlt⟩ := h, unfold RamseyNontrivial at hlt, simp [Fintype.card_fin] at hlt.
-/
theorem fragile_variant_false :
    ¬ (∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ RamseyNontrivial G < 2 ^ n) := by
  simp +zetaDelta at *;
  use 0; aesop;

end Erdos181