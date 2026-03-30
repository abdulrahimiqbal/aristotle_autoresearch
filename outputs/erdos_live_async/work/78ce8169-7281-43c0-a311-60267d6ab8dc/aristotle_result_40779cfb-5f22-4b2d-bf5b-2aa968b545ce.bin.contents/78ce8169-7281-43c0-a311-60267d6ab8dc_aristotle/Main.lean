/-
Experiment ID: 78ce8169-7281-43c0-a311-60267d6ab8dc
Move: reformulate
Move family: extremal_case
Theorem family: erdos_problem
Phase: consolidation
Modification: {"extremal_target": "ed to recover a non-trivial (and currently open) conjecture."}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- extremal sweep: ed to recover a non-trivial (and currently open) conjecture.
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
statement used on erdosproblems.com.

With the placeholder definitions (`GraphRamseyNumber := 0`, `IsHypercubeGraph := True`),
this statement is trivially true. -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-!
## Reformulated extremal conjecture

Erdős Problem 181 asks whether the two-colour Ramsey number `R(Qₙ)` of the
`n`-dimensional hypercube graph satisfies `R(Qₙ) ≤ C · 2ⁿ` for some absolute
constant `C`.  The **extremal boundary** of this conjecture is obtained by pushing
the multiplicative constant `C` down to `1 + ε` for every `ε > 0` and all
sufficiently large `n`.  Concretely, this asks:

> **Conjecture (Extremal Erdős 181).**
> For every `ε > 0`, there exists `N₀` such that for all `n ≥ N₀`,
> the Ramsey number of the `n`-dimensional hypercube satisfies
> `R(Qₙ) ≤ ⌈(1 + ε) · 2ⁿ⌉`.

This is a strictly stronger (and still open) refinement of the original problem.
If true, it says that asymptotically a two-colouring of the edges of `Kₘ` with
`m` just barely larger than `2ⁿ` already forces a monochromatic copy of `Qₙ`.

Below we formalise this extremal reformulation.  Because the Ramsey-number
infrastructure is still a placeholder, we state the conjecture using an abstract
`ramseyNumber` function supplied as a parameter, making the statement non-trivially
falsifiable (it cannot be discharged by unfolding a definition to `0`).
-/

/-- **Extremal Erdős 181 conjecture.**

For every `ε > 0` and all sufficiently large `n`, the two-colour Ramsey number of
the `n`-dimensional hypercube `Qₙ` satisfies `R(Qₙ) ≤ ⌈(1 + ε) · 2ⁿ⌉`.

`ramseyNumber` is taken as a parameter so that the statement is non-trivial:
it cannot be proved or disproved merely by unfolding a placeholder definition. -/
def extremal_erdos_181_conjecture (ramseyNumber : ℕ → ℕ) : Prop :=
  ∀ ε : ℝ, 0 < ε →
    ∃ N₀ : ℕ, ∀ n : ℕ, N₀ ≤ n →
      (ramseyNumber n : ℝ) ≤ (1 + ε) * (2 : ℝ) ^ n

/-- The original Erdős 181 conjecture (linear upper bound) follows from the
extremal version by specialising `ε = 1`. -/
theorem extremal_implies_original (ramseyNumber : ℕ → ℕ)
    (h : extremal_erdos_181_conjecture ramseyNumber) :
    ∃ C : ℝ, 0 < C ∧ ∃ N₀ : ℕ, ∀ n : ℕ, N₀ ≤ n →
      (ramseyNumber n : ℝ) ≤ C * (2 : ℝ) ^ n := by
  obtain ⟨ N₀, hN₀ ⟩ := h 1 zero_lt_one ; exact ⟨ 2, by norm_num, N₀, fun n hn => by have := hN₀ n hn; norm_num at * ; linarith ⟩ ;

end Erdos181