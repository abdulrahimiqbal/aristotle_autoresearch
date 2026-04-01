/-
Experiment ID: 2bad792c-15a9-4fac-83dc-941947f74e6d
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 42, "target": "boundary_variant"}
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
A self-contained Lean 4 stub for Erdos Problem 181, modeled on the informal
statement used on erdosproblems.com.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 1
  simp [IsHypercubeGraph, GraphRamseyNumber]

/-! ## Boundary variant analysis

We investigate what happens when the bound `C * 2^n` is replaced by
the *strict* inequality `< 2^n` (i.e., asking for a *sub-exponential* Ramsey
number).  With the current placeholder definitions (`GraphRamseyNumber := 0`,
`IsHypercubeGraph := True`), every proposed tightening is vacuously true,
demonstrating that the placeholders cannot distinguish the original statement
from its boundary variants.

### Variant 1 – Constant bound (much stronger than original)
Asking `GraphRamseyNumber G ≤ C` (independent of `n`).
-/

/-
**Boundary variant 1 (constant bound):** With placeholder definitions, even
the absurdly strong statement that the Ramsey number is bounded by a constant
independent of the dimension `n` is provable, because `GraphRamseyNumber = 0`.
-/
theorem boundary_constant_bound :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C := by
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, trivial, by unfold GraphRamseyNumber; norm_num ⟩ ⟩

/-! ### Variant 2 – Zero Ramsey number
The strongest possible tightening: asking `GraphRamseyNumber G = 0`.
This is trivially provable with the placeholder. -/

/-
**Boundary variant 2 (zero bound):** `GraphRamseyNumber` is identically 0
under the placeholder definition.
-/
theorem boundary_zero_ramsey :
    ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      GraphRamseyNumber G = 0 := by
  exact fun n G => Nat.eq_zero_of_add_eq_zero_left rfl

/-! ### Variant 3 – Lower bound (counterexample search)
The *negation* of a polynomial lower bound: we show that under the placeholder,
no graph has `GraphRamseyNumber G ≥ 1`, which witnesses that the placeholder
cannot model the expected superlinear growth of the true Ramsey number. -/

/-
**Boundary variant 3 (no lower bound):** Under the placeholder, there is
no graph whose Ramsey number is at least 1, providing a concrete
counterexample-witness showing the placeholder is too degenerate to
support a lower-bound formulation.
-/
theorem boundary_no_lower_bound :
    ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      ¬(1 ≤ GraphRamseyNumber G) := by
  exact fun n G => Nat.not_succ_le_self 0

/-! ### Variant 4 – Boundary at `C = 0`
Testing whether the existential constant can be pushed to `C = 0`.
With the placeholder this succeeds, whereas in the *true* problem
`R(Q_n) ≥ 1` for all `n ≥ 1`, so one needs `C ≥ 1`. -/

/-
**Boundary variant 4 (`C = 0` boundary):** The original theorem requires
`1 ≤ C`.  With the placeholder, even `C = 0` works, showing the `1 ≤ C`
guard is vacuously satisfiable.
-/
theorem boundary_C_eq_zero :
    ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ 0 := by
  exact fun n => ⟨ ⊥, trivial, by rfl ⟩

end Erdos181