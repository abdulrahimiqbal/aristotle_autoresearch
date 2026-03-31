/-
Experiment ID: c59a7825-18a0-4631-97a4-992eced2afcd
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 37, "target": "boundary_variant"}
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
IsHypercubeGraph is defined as True and GraphRamseyNumber is defined as 0. So pick C = 1. For any n, use the empty graph ⊥. Then IsHypercubeGraph n ⊥ is trivial and GraphRamseyNumber ⊥ = 0 ≤ 1 * 2^n. Use exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 1;
  refine' ⟨ by norm_num, _ ⟩;
  intro n;
  refine' ⟨ ⊥, _, _ ⟩;
  · constructor;
  · exact Nat.zero_le _

/-!
## Boundary variant

The natural "boundary variant" of the Erdős hypercube Ramsey problem asks whether the
Ramsey number of Q_n is *at least* `2^n`, i.e., whether the upper bound `C · 2^n` is
tight up to a constant.  With the current placeholder definitions (`GraphRamseyNumber = 0`
and `IsHypercubeGraph = True`), this lower-bound statement is **false**: a concrete
counterexample exists at `n = 1` (or any `n ≥ 1`), since `GraphRamseyNumber G = 0 < 2^n`.

We formalize the boundary variant and provide an explicit counterexample (disproof).
-/

/-- Boundary variant: "For every `n ≥ 1`, every hypercube graph has Ramsey number ≥ 2^n."
With the placeholder definitions this is **false**. -/
def boundary_variant : Prop :=
  ∀ n : ℕ, 1 ≤ n → ∀ G : SimpleGraph (Fin (2 ^ n)),
    IsHypercubeGraph n G → 2 ^ n ≤ GraphRamseyNumber G

/-
PROBLEM
The boundary variant is false under the placeholder definitions:
`GraphRamseyNumber` is always `0`, so `2^n ≤ 0` fails for `n ≥ 1`.

PROVIDED SOLUTION
Unfold boundary_variant. Specialize at n = 1 with G = ⊥. IsHypercubeGraph 1 ⊥ is True (trivial). The conclusion would be 2^1 ≤ GraphRamseyNumber ⊥, i.e. 2 ≤ 0 (since GraphRamseyNumber is defined as 0). This is a contradiction. So intro h, apply h at n=1 with ⊥ and trivial, then the result 2 ≤ 0 gives omega or Nat.not_succ_le_zero.
-/
theorem boundary_variant_false : ¬ boundary_variant := by
  -- Assume the boundary variant is true.
  by_contra h
  simp_all +decide [ boundary_variant ];
  have := h 1 le_rfl;
  exact absurd ( this ⊥ trivial ) ( by unfold GraphRamseyNumber; norm_num )

end Erdos181