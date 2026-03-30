/-
Experiment ID: 2d583909-5498-4b4e-8504-10dc3e0f5939
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "most_fragile_variant"}
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
Use C = 1. For any n, take G = ⊥ (the empty graph). Then IsHypercubeGraph n G = True (by definition), and GraphRamseyNumber G = 0 (by definition), so 0 ≤ 1 * 2^n.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Let's choose C = 2.
  use 2;
  -- Show that $1 \leq 2$.
  simp [IsHypercubeGraph, GraphRamseyNumber]

/-!
## Fragility analysis

The theorem above is trivially true because:
- `IsHypercubeGraph` is defined as `True`, so *any* graph witnesses the existential.
- `GraphRamseyNumber` is defined as `0`, so the bound `0 ≤ C * 2^n` holds for any `C`.

Below we demonstrate this fragility:
1. `erdos_181_trivial_proof` proves the theorem exploiting the placeholders.
2. We define a non-trivial `GraphRamseyNumber'` that grows super-linearly,
   and prove the analogous statement is *false* — a formal counterexample
   witnessing the fragility of the "most fragile observed variant."
-/

/-
PROBLEM
The original statement is trivially true with the placeholder definitions.

PROVIDED SOLUTION
Use C = 1. For any n, take G = ⊥ (the empty graph). Then IsHypercubeGraph n G = True (by definition), and GraphRamseyNumber G = 0 (by definition), so 0 ≤ 1 * 2^n.
-/
theorem erdos_181_trivial_proof :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact erdos_181_hypercube_ramsey

/-! ### Falsifying witness for a non-trivial variant -/

/-- A non-trivial Ramsey number placeholder that grows super-linearly in the
number of vertices: `GraphRamseyNumber' G = (Fintype.card α)^2`.
With `α = Fin (2^n)`, this gives `(2^n)^2 = 2^(2n)`, which grows much faster
than any `C * 2^n`. -/
def GraphRamseyNumber' {α : Type*} [Fintype α] (_G : SimpleGraph α) : ℕ :=
  (Fintype.card α) ^ 2

/-
PROBLEM
With a super-linearly growing Ramsey number, no constant `C` can bound
`R(Qₙ) ≤ C · 2ⁿ` for all `n`. This is the falsifying witness.

PROVIDED SOLUTION
Unfold the negation. Given C ≥ 1 and the universal statement, specialize at n = 2*C (or some large enough n). For any G on Fin (2^n), GraphRamseyNumber' G = (2^n)^2 = 2^(2n). The bound says 2^(2n) ≤ C * 2^n, i.e. 2^n ≤ C. But for n large enough (n ≥ C+1 suffices since 2^(C+1) > C for C ≥ 1), this is a contradiction. So push_neg, intro C, intro hC, choose n large enough, and show the contradiction.
-/
theorem erdos_181_false_with_nontrivial_ramsey :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber' G ≤ C * 2 ^ n) := by
  simp +zetaDelta at *;
  intro x hx; use x + 1; intro G hG; unfold IsHypercubeGraph at hG; unfold GraphRamseyNumber' at *; norm_num at *; (
  nlinarith [ show x < 2 ^ ( x + 1 ) by exact Nat.recOn x ( by norm_num ) fun n ihn => by norm_num [ Nat.pow_succ' ] at * ; linarith ]);

end Erdos181