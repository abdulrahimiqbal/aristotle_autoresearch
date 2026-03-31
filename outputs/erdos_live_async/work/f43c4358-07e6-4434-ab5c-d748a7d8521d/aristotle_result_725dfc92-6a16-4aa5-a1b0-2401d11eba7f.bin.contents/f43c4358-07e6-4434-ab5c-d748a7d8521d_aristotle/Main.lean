/-
Experiment ID: f43c4358-07e6-4434-ab5c-d748a7d8521d
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 38, "target": "minimal_variant"}
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
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, by unfold IsHypercubeGraph; norm_num,
    by unfold GraphRamseyNumber; norm_num ⟩ ⟩

/-! ## Minimal variant exploration

The "minimal variant" attempts to strengthen the original statement. We explore
several natural strengthenings and show which are provable (with the placeholder
definitions) and which admit counterexamples.
-/

/-! ### Variant 1: Counterexample — C = 0 is impossible

The original statement requires `1 ≤ C`. If we try C = 0, the condition `1 ≤ 0`
is false, so no witness exists with C = 0. We prove this negation. -/

/-
PROVIDED SOLUTION
The first component of the conjunction is 1 ≤ 0, which is false. So intro ⟨h, _⟩ and use omega or Nat.not_succ_le_zero on h.
-/
theorem erdos_181_no_C_zero :
    ¬(1 ≤ (0 : ℕ) ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ 0 * 2 ^ n) := by
  norm_num

/-! ### Variant 2: Universal variant (for all G, not just ∃ G)

The original only asks for the *existence* of a hypercube graph with a small
Ramsey number. A stronger "universal" variant asks that *every* hypercube graph
has a small Ramsey number. With the placeholder definitions this is still true. -/

/-
PROVIDED SOLUTION
Pick C = 1. For any G, GraphRamseyNumber G = 0 by definition, so 0 ≤ 1 * 2^n. exact ⟨1, le_refl 1, fun n G _ => by unfold GraphRamseyNumber; exact Nat.zero_le _⟩
-/
theorem erdos_181_universal_variant :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → GraphRamseyNumber G ≤ C * 2 ^ n := by
  unfold GraphRamseyNumber; aesop;

/-! ### Variant 3: Minimal C is 1

C = 1 is the minimal valid constant under the current placeholder definitions,
since any valid C must satisfy `1 ≤ C`. -/

/-
PROVIDED SOLUTION
Trivial: the hypothesis contains 1 ≤ C as its first conjunct, so just extract it. intro C ⟨h, _⟩; exact h
-/
theorem erdos_181_minimal_C :
    ∀ C : ℕ, (1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n) → 1 ≤ C := by
  exact fun C hC => hC.1

/-! ### Variant 4: Strict bound

Strengthening to strict inequality `<` instead of `≤`. With placeholders
(GraphRamseyNumber = 0), we need `0 < C * 2^n`. Since C ≥ 1 and 2^n ≥ 1,
this holds. -/

/-
PROVIDED SOLUTION
Pick C = 1, G = ⊥. Need 0 < 1 * 2^n, i.e. 0 < 2^n which is Nat.pos_of_ne_zero or positivity. GraphRamseyNumber is 0 by definition. exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, by unfold GraphRamseyNumber; positivity⟩⟩
-/
theorem erdos_181_strict_bound :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G < C * 2 ^ n := by
  -- Let's choose C = 1.
  use 1
  simp [IsHypercubeGraph, GraphRamseyNumber] at *

/-! ### Variant 5: Counterexample witness — dropping `1 ≤ C` makes C = 0 valid

If we remove the constraint `1 ≤ C`, then C = 0 works trivially, showing the
`1 ≤ C` constraint is necessary for non-degeneracy. -/

/-
PROVIDED SOLUTION
For each n, pick G = ⊥. IsHypercubeGraph is True, and GraphRamseyNumber G = 0 ≤ 0 * 2^n = 0. intro n; exact ⟨⊥, trivial, by unfold GraphRamseyNumber; simp⟩
-/
theorem erdos_181_degenerate_C_zero :
    ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ 0 * 2 ^ n := by
  exact fun n => ⟨ ⊥, trivial, by unfold GraphRamseyNumber; simp ⟩

end Erdos181