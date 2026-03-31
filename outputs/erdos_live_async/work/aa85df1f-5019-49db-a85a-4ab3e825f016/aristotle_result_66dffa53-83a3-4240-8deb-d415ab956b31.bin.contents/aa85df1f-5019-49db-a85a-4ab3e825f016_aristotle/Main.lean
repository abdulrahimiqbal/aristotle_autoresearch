/-
Experiment ID: aa85df1f-5019-49db-a85a-4ab3e825f016
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 36, "target": "most_fragile_variant"}
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

theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 1;
  simp [IsHypercubeGraph, GraphRamseyNumber]

/-!
## Most fragile variant: counterexample analysis

The theorem above is trivially true because `GraphRamseyNumber` is defined as `0`.
The "most fragile variant" is obtained by replacing the placeholder with a
*non-trivial* Ramsey number lower bound.

Below we instantiate `GraphRamseyNumber` with the value `2 ^ n` (the number of
vertices of the hypercube), which models the well-known fact that
`R(Q_n) ≥ 2^n` (a graph on `2^n` vertices trivially needs at least `2^n` colors
in the Ramsey sense).  Under this instantiation, the "strict sub-exponential" variant
`R(Q_n) ≤ C` (for any fixed `C`) fails for large `n`, and the variant with
`C = 0` also fails.  We formalize these counterexamples.
-/

/-- A non-trivial Ramsey number model: returns `2^n`, modeling the trivial lower
bound `R(Q_n) ≥ 2^n`. -/
def GraphRamseyNumber' (n : ℕ) : ℕ := 2 ^ n

/-
PROBLEM
**Fragile variant 1 (C = 0):** With a non-trivial Ramsey number, requiring
`GraphRamseyNumber' n ≤ 0` is false for all `n`.

PROVIDED SOLUTION
GraphRamseyNumber' n = 2^n. For n=0, 2^0=1>0, so the universal statement fails. intro h; have := h 0; simp [GraphRamseyNumber'] at this.
-/
theorem fragile_variant_C_zero_false : ¬ (∀ n : ℕ, GraphRamseyNumber' n ≤ 0) := by
  -- By definition of GraphRamseyNumber', we know that 2^n ≤ GraphRamseyNumber' n for all n.
  simp [GraphRamseyNumber'] at *

/-
PROBLEM
**Fragile variant 2 (bounded by a constant):** No fixed constant `C` can bound
`2^n` for all `n`. This is the key failure mode of the "most fragile" strengthening
where one tries to make the Ramsey number bounded rather than linear in `2^n`.

PROVIDED SOLUTION
Assume ⟨C, h⟩. Then for n = C+1 (or any large enough n), 2^n > C, contradicting h n. Use Nat.lt_two_pow or similar to get 2^(C+1) > C. Unfold GraphRamseyNumber' and derive contradiction.
-/
theorem fragile_variant_bounded_false :
    ¬ (∃ C : ℕ, ∀ n : ℕ, GraphRamseyNumber' n ≤ C) := by
  -- Assume for contradiction that there exists a constant $C$ such that $2^n \leq C$ for all $n$.
  by_contra h
  obtain ⟨C, hC⟩ := h;
  exact absurd ( hC ( Nat.log 2 C + 1 ) ) ( by rw [ show GraphRamseyNumber' ( Nat.log 2 C + 1 ) = 2 ^ ( Nat.log 2 C + 1 ) by rfl ] ; exact Nat.not_le_of_gt ( Nat.lt_pow_succ_log_self ( by decide ) _ ) )

/-
PROBLEM
**Original variant still holds with the non-trivial model:** With `R(Q_n) = 2^n`,
the original linear bound `R(Q_n) ≤ C · 2^n` holds with `C = 1`. This shows the
original formulation sits exactly at the boundary.

PROVIDED SOLUTION
Use C = 1. Then 1 ≤ 1 is trivial, and GraphRamseyNumber' n = 2^n ≤ 1 * 2^n = 2^n. Unfold GraphRamseyNumber' and use le_refl.
-/
theorem original_variant_still_holds :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, GraphRamseyNumber' n ≤ C * 2 ^ n := by
  exact ⟨ 1, by norm_num, fun n => by unfold GraphRamseyNumber'; norm_num ⟩

end Erdos181