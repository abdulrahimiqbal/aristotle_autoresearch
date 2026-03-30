/-
Experiment ID: d94cc062-d56a-450a-aad0-e6ec7d2dca38
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
Use C = 1. For any n, take G = ⊥ (the empty graph). IsHypercubeGraph n G unfolds to True, and GraphRamseyNumber G unfolds to 0. So 0 ≤ 1 * 2^n by Nat.zero_le.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  refine' ⟨ 1, by norm_num, _ ⟩;
  intro n
  use ⊥;
  exact ⟨ trivial, by norm_num [ GraphRamseyNumber ] ⟩

/-! ## Fragility analysis

The definitions `IsHypercubeGraph` and `GraphRamseyNumber` are placeholders.
`IsHypercubeGraph` is literally `True`, and `GraphRamseyNumber` is literally `0`.
This makes the above theorem trivially true — a **falsifying witness** for the
claim that this formalization captures any mathematical content.

### Witness 1: The theorem is trivially provable

We prove it directly, exposing the vacuity.
-/

/-
PROBLEM
The theorem is trivially true because `GraphRamseyNumber` is always `0` and
`IsHypercubeGraph` is always `True`. This is a witness to the fragility of
the formalization: it "proves" an open problem by exploiting placeholder definitions.

PROVIDED SOLUTION
Use C = 1. For any n, take G = ⊥ (the empty graph). IsHypercubeGraph n G unfolds to True, and GraphRamseyNumber G unfolds to 0. So 0 ≤ 1 * 2^n by Nat.zero_le.
-/
theorem erdos_181_trivially_true :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Fix an arbitrary $C \geq 1$.
  use 1; simp [IsHypercubeGraph, GraphRamseyNumber]

/-! ### Witness 2: Independence-style witness

If we strengthen `GraphRamseyNumber` to return *any* fixed positive value instead
of `0`, the statement becomes sensitive to the actual Ramsey-theoretic content.
We define a "strengthened" variant where `GraphRamseyNumber` is replaced by a
function that returns `2^(2^n)` (a super-exponential value), and show the
analogous statement is *false* — no linear bound `C * 2^n` can work.

This demonstrates independence from the proof-irrelevant placeholder: the truth
value of the theorem depends entirely on the (currently trivial) definition of
`GraphRamseyNumber`.
-/

/-- A non-trivial substitute for `GraphRamseyNumber` that returns a super-exponential
value, modeling a scenario where Ramsey numbers grow faster than linearly in `2^n`. -/
def GraphRamseyNumber_Strong (n : ℕ) : ℕ := 2 ^ (2 ^ n)

/-
PROBLEM
With the strengthened Ramsey number, no constant `C` can bound `2^(2^n)` by
`C * 2^n` for all `n`. This is the independence-style witness: swapping the
placeholder for anything non-trivial can flip the truth value.

PROVIDED SOLUTION
Unfold GraphRamseyNumber_Strong. Push negation: need to show for all C ≥ 1, there exists n such that 2^(2^n) > C * 2^n. Given C, pick n large enough. For n ≥ 1, 2^n ≥ n+1, so 2^(2^n) ≥ 2^(n+1) = 2*2^n. More precisely, for any C, take n such that 2^n > n + log2(C). Then 2^(2^n) > C * 2^n. Alternatively: pick n = C. Then 2^(2^C) vs C * 2^C. Since 2^C ≥ C+1 for C ≥ 1, we get 2^(2^C) ≥ 2^(C+1) = 2*2^C ≥ (C+1)*2 > C for C ≥ 1... actually we need 2^(2^C) > C * 2^C, i.e. 2^(2^C - C) > C. Since 2^C - C ≥ C for C ≥ 2 (and 2^1-1=1, 2^1=2>1=C for C=1), we get 2^(2^C-C) ≥ 2^C ≥ C+1 > C. So specializing at n = C works.
-/
theorem erdos_181_strong_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ,
      GraphRamseyNumber_Strong n ≤ C * 2 ^ n) := by
  push_neg;
  intro C hC
  use C + 1
  simp [GraphRamseyNumber_Strong];
  induction' hC with C hC ih <;> norm_num [ Nat.pow_succ', Nat.pow_mul ] at *;
  rw [ show 16 = 4 ^ 2 by norm_num, pow_right_comm ];
  nlinarith [ Nat.pow_le_pow_right ( show 1 ≤ 2 by norm_num ) hC, Nat.mul_le_mul_left ( 2 ^ C ) hC ]

end Erdos181