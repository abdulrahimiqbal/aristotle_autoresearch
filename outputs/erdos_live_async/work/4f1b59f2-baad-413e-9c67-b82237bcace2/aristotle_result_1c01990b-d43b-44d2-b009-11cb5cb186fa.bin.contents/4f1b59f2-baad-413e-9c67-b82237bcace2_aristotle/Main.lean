/-
Experiment ID: 4f1b59f2-baad-413e-9c67-b82237bcace2
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 39, "target": "negated_weakening"}
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
  exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-! ## Negated weakening

A natural "negated weakening" of the above statement strengthens the existential to a
universal: it asks whether **every** hypercube graph has Ramsey number at most `C · 2^n`.
Because `IsHypercubeGraph` is the trivial predicate `True` and `GraphRamseyNumber` is
the constant `0`, this negated-universal version is **also** true with the current
placeholders — there is no genuine counterexample under these definitions.

We record this observation as a theorem (the "would-be negation" is actually false,
i.e. the universal statement holds) and provide a concrete witness showing why
the negation fails.
-/

/-
PROBLEM
The negated weakening: "there is no uniform constant bounding the Ramsey number of
every hypercube graph."  With the placeholder definitions this is **false** — we disprove
it by exhibiting `C = 1`.

PROVIDED SOLUTION
Push the negation: we need to show ∃ C, 1 ≤ C ∧ ∀ n G, IsHypercubeGraph n G → GraphRamseyNumber G ≤ C * 2^n. Use C = 1. GraphRamseyNumber is defined as 0, so GraphRamseyNumber G = 0 ≤ 1 * 2^n. IsHypercubeGraph is True.
-/
theorem negated_weakening :
    ¬ (∀ C : ℕ, 1 ≤ C → ∃ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → C * 2 ^ n < GraphRamseyNumber G) := by
  simp +zetaDelta at *;
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, trivial, by unfold GraphRamseyNumber; norm_num ⟩ ⟩

/-
PROBLEM
Independence-style witness: the universal version of the bound holds for `C = 1`
under the placeholder definitions, providing the concrete refutation used above.

PROVIDED SOLUTION
GraphRamseyNumber G = 0 by definition (unfold GraphRamseyNumber), so 0 ≤ 1 * 2^n. Just intro everything, unfold GraphRamseyNumber, and use Nat.zero_le.
-/
theorem universal_bound_witness :
    ∀ n : ℕ, ∀ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G → GraphRamseyNumber G ≤ 1 * 2 ^ n := by
  unfold IsHypercubeGraph GraphRamseyNumber at *; aesop;

end Erdos181