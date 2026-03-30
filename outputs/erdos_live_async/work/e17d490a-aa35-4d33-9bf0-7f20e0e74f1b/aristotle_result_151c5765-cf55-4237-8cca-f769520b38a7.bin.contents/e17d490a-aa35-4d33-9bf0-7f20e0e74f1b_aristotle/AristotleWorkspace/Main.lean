/-
Experiment ID: e17d490a-aa35-4d33-9bf0-7f20e0e74f1b
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
Pick C = 1, for any n use G = ⊥. Unfold IsHypercubeGraph to True, unfold GraphRamseyNumber to 0. Then 0 ≤ 1 * 2^n is obvious.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- We can choose C = 1 since 1 * 2^n = 2^n, and the inequality holds trivially for n = 0 and n = 1.
  use 1
  simp [IsHypercubeGraph, GraphRamseyNumber] at *

/-!
## Fragility witness

The theorem above is trivially true because both placeholder definitions
are degenerate:

- `IsHypercubeGraph n G := True` — every graph vacuously satisfies this.
- `GraphRamseyNumber G := 0` — every graph has Ramsey number zero.

We demonstrate this fragility in two ways:

1. **Trivial proof**: we prove the theorem as stated, showing the placeholders
   render it content-free.

2. **Counterexample under a non-trivial variant**: we define an alternative
   `GraphRamseyNumber'` that grows super-exponentially and show that the
   analogous statement is *false*, witnessing that the original theorem's
   truth depends entirely on the degeneracy of the placeholders.
-/

/-
PROBLEM
The original theorem is trivially true: pick `C = 1` and any graph `G`;
`IsHypercubeGraph` is `True` and `GraphRamseyNumber` is `0`.

PROVIDED SOLUTION
Same as erdos_181_hypercube_ramsey: pick C = 1, G = ⊥, unfold defs, trivial.
-/
theorem erdos_181_trivial_proof :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, trivial, by unfold GraphRamseyNumber; norm_num ⟩ ⟩

/-! ### Non-trivial variant: independence-style witness -/

/-- A non-degenerate "Ramsey number" placeholder that grows as `(2^n)!`,
which is super-exponential and cannot be bounded by `C · 2^n`. -/
def GraphRamseyNumber' {α : Type*} [Fintype α] (_G : SimpleGraph α) : ℕ :=
  (Fintype.card α).factorial

/-
PROBLEM
With `GraphRamseyNumber'`, the analogous statement is false:
no constant `C` can bound `(2^n)!` by `C * 2^n` for all `n`.

PROVIDED SOLUTION
Assume ⟨C, hC1, hf⟩. Specialize hf at some large n. For any G on Fin (2^n), GraphRamseyNumber' G unfolds to (Fintype.card (Fin (2^n))).factorial = (2^n).factorial (use Fintype.card_fin). IsHypercubeGraph is True so the hypothesis gives (2^n)! ≤ C * 2^n. But for n large enough (try n = C + 3 or similar), (2^n)! > C * 2^n. Use Nat.factorial_lt or show 2^n ≥ 2 so (2^n)! ≥ (2^n) * (2^n - 1)! ≥ 2^n * 1 and actually much more. For a concrete approach: take n such that 2^n > C (exists by Nat.lt_two_pow or similar), then (2^n)! ≥ (2^n) * ((2^n - 1)!) ≥ (2^n) * 1 and actually (2^n)! ≥ (2^n)^2 when 2^n ≥ 2 since (2^n)! = (2^n)(2^n-1)... ≥ (2^n) * (2^n - 1) ≥ (2^n) * (2^n / 2) when 2^n ≥ 2. So (2^n)! ≥ 2^(2n-1). We need 2^(2n-1) > C * 2^n, i.e. 2^(n-1) > C, which holds for n large enough. Key lemma: Nat.factorial_pos, and that k! ≥ k for k ≥ 1, actually k! ≥ 2^(k-1) for k ≥ 1 by induction. Then (2^n)! ≥ 2^(2^n - 1) which is way more than C * 2^n for large n.
-/
theorem erdos_181_variant_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber' G ≤ C * 2 ^ n) := by
  by_contra h_contra
  obtain ⟨C, hC1, hC⟩ := h_contra;
  obtain ⟨G, hG1, hG2⟩ := hC (C + 5);
  -- For n large enough, (2^n)! > C * 2^n. Use this fact.
  have h_factorial_growth : (2 ^ (C + 5)).factorial > C * 2 ^ (C + 5) := by
    refine' Nat.le_induction _ _ _ ( show C ≥ 1 from hC1 ) <;> intros <;> simp_all +decide [ Nat.pow_succ', Nat.factorial_succ ];
    rename_i k hk₁ hk₂;
    refine' lt_of_lt_of_le _ ( Nat.factorial_le ( show 2 * ( 2 * ( 2 * ( 2 * ( 2 * ( 2 * 2 ^ k ) ) ) ) ) ≥ 2 * ( 2 * ( 2 * ( 2 * ( 2 * 2 ^ k ) ) ) ) + 1 by linarith [ pow_pos ( zero_lt_two' ℕ ) k ] ) );
    norm_num [ Nat.factorial_succ ] at *;
    nlinarith [ Nat.mul_le_mul_left ( 2 * ( 2 * ( 2 * ( 2 * ( 2 * 2 ^ k ) ) ) ) ) hk₁, Nat.one_le_pow k 2 zero_lt_two ];
  contrapose! hG2;
  unfold GraphRamseyNumber' ; aesop

end Erdos181