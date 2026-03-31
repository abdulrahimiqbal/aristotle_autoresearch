/-
Experiment ID: 8f2ea3e5-4cb8-438a-b5e4-b5505a4d6a00
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 33, "target": "minimal_variant"}
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
Since IsHypercubeGraph is True and GraphRamseyNumber is 0, use C = 1. For any n, use the empty SimpleGraph (⊥). Then IsHypercubeGraph n ⊥ unfolds to True (trivial), and GraphRamseyNumber ⊥ unfolds to 0, so 0 ≤ 1 * 2^n by Nat.zero_le.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  refine' ⟨ 1, by norm_num, _ ⟩;
  exact fun n => ⟨ ⊥, trivial, by simp +decide [ GraphRamseyNumber ] ⟩

/-
PROBLEM
**Minimal variant (lower bound)**: Can we also show that the Ramsey number of every
hypercube graph is *at least* `C * 2^n` for some positive `C`?  With the current
placeholder (`GraphRamseyNumber = 0`), this is **false** for every `C ≥ 1` because
`C * 2^0 = C ≥ 1 > 0 = GraphRamseyNumber _`.  The following gives a formal
counterexample.

PROVIDED SOLUTION
Intro ⟨C, hC, hAll⟩. Specialize hAll at n = 0 with G = ⊥. Since IsHypercubeGraph 0 ⊥ is True (trivial), we get C * 2^0 ≤ GraphRamseyNumber ⊥. But GraphRamseyNumber ⊥ unfolds to 0, and C * 2^0 = C * 1 = C ≥ 1 > 0. This gives 1 ≤ 0, a contradiction. Use omega or Nat.not_succ_le_zero.
-/
theorem erdos_181_lower_bound_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → C * 2 ^ n ≤ GraphRamseyNumber G) := by
  simp +zetaDelta at *;
  intro C hC; use 0; use ⊥; simp +decide [ *, IsHypercubeGraph, GraphRamseyNumber ] ;
  linarith

/-
PROBLEM
Even the weakened existential lower-bound variant (there *exists* a hypercube
graph whose Ramsey number is at least `C * 2^n`) is false with the placeholder,
because `GraphRamseyNumber` is identically `0`.

PROVIDED SOLUTION
Intro ⟨C, hC, hAll⟩. Specialize hAll at n = 0 to get ⟨G, _, hle⟩. GraphRamseyNumber G unfolds to 0, and C * 2^0 = C ≥ 1. So we get 1 ≤ 0, contradiction. Use omega/simp [GraphRamseyNumber] after obtaining the pieces.
-/
theorem erdos_181_existential_lower_bound_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ C * 2 ^ n ≤ GraphRamseyNumber G) := by
  unfold IsHypercubeGraph GraphRamseyNumber;
  aesop

end Erdos181