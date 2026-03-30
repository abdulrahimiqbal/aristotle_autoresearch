/-
Experiment ID: 7a1440ba-0f7c-49b7-a47e-7d614b3840a6
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

/-- A self-contained Lean 4 stub for Erdős Problem 181, modeled on the informal
statement used on erdosproblems.com.

**Independence witness**: With the placeholder definitions (`IsHypercubeGraph := True`,
`GraphRamseyNumber := 0`), this theorem is vacuously true and entirely independent of
the intended Ramsey-theoretic content. Any `C ≥ 1` and any graph `G` witness it. -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-!
## Fragility analysis

The definitions above are placeholders:
- `IsHypercubeGraph n G` unfolds to `True`, so the existential `∃ G, ...` imposes
  no structural constraint — *any* simple graph witnesses it.
- `GraphRamseyNumber G` unfolds to `0`, so the Ramsey-number bound `0 ≤ C * 2 ^ n`
  is trivially satisfied for every `C ≥ 1`.

Together these make `erdos_181_hypercube_ramsey` vacuously true and entirely
independent of the intended Ramsey-theoretic content.

### Falsifying variant — Non-trivial `GraphRamseyNumber` breaks the statement

If one replaces the Ramsey-number placeholder with any super-exponential function
(e.g., `2 ^ Fintype.card α`, which evaluates to `2 ^ 2^n` on `Fin (2^n)`), the
analogous statement is provably *false*: no single constant `C` can satisfy
`2^(2^n) ≤ C * 2^n` for all `n`, since the left side grows doubly-exponentially
while the right side grows only singly-exponentially.
-/

/-- A "non-trivial" Ramsey-number placeholder that grows super-exponentially. -/
def GraphRamseyNumber' {α : Type*} [Fintype α] (G : SimpleGraph α) : ℕ :=
  2 ^ Fintype.card α

/-- **Falsifying witness** for the most fragile observed variant:
with `GraphRamseyNumber'` replacing `GraphRamseyNumber`, the statement is *false*.
For any proposed constant `C`, specialising at `n = C` yields `2^(2^C) ≤ C * 2^C`,
which fails because `2^(2^C) > C * 2^C` for all `C ≥ 1`. -/
theorem erdos_181_variant_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber' G ≤ C * 2 ^ n) := by
  simp +decide [IsHypercubeGraph, GraphRamseyNumber']
  intro x hx; use x; ring_nf
  induction hx <;> simp_all +decide [pow_succ, pow_mul]
  rename_i k hk ih
  nlinarith [Nat.pow_le_pow_right (show 1 ≤ 2 by norm_num) hk,
             Nat.mul_le_mul_left (2 ^ k) hk]

end Erdos181
