/-
Experiment ID: 2f01e299-842e-443f-b056-e965f5f690b8
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "minimal_variant", "attempt": 18}
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
With the placeholder definitions, IsHypercubeGraph is always True and GraphRamseyNumber is always 0. So take C = 1. For each n, take G = ⊥ (emptyGraph). IsHypercubeGraph unfolds to True, and GraphRamseyNumber unfolds to 0, so the bound 0 ≤ 1 * 2^n is trivial.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  use 1
  simp_all +decide [Erdos181.IsHypercubeGraph, Erdos181.GraphRamseyNumber]

/-!
## Minimal variant: counterexample search

The original theorem is trivially true because `GraphRamseyNumber` always returns `0`.
The "minimal variant" asks: what is the weakest non-trivial change to the placeholders
that makes the statement false?

**Minimal variant 1**: Replace `GraphRamseyNumber` with one that returns a superlinear
function of the vertex count, e.g. `(Fintype.card α) ^ 2`. Then the statement becomes
false because `(2^n)^2 = 4^n` grows faster than any `C * 2^n`.

**Minimal variant 2**: Keep `GraphRamseyNumber := 0` but strengthen the statement to
require `C = 0` (i.e., `GraphRamseyNumber G = 0` for some hypercube graph, which is
trivially true) — too weak to be interesting.

We formalize Minimal variant 1 below.
-/

/-- A "non-trivial" Ramsey-number placeholder that returns the square of the vertex count.
This models a Ramsey number growing superlinearly in the number of vertices. -/
def GraphRamseyNumberSuperlinear {α : Type*} [Fintype α] (_G : SimpleGraph α) : ℕ :=
  (Fintype.card α) ^ 2

/-
PROBLEM
The minimal variant with a superlinear Ramsey number is **false**: no constant `C`
can make `(2^n)^2 ≤ C * 2^n` hold for all `n`, since this would require `2^n ≤ C`
for all `n`.

PROVIDED SOLUTION
Push the negation inside: we need to show for any C ≥ 1, there exists n such that for all G : SimpleGraph (Fin (2^n)), either ¬IsHypercubeGraph n G ∨ GraphRamseyNumberSuperlinear G > C * 2^n. Since IsHypercubeGraph is True, the first disjunct never fires. So we need (2^n)^2 > C * 2^n for some n. Note Fintype.card (Fin (2^n)) = 2^n, so GraphRamseyNumberSuperlinear G = (2^n)^2. We need (2^n)^2 > C * 2^n, i.e., 2^n > C. Take n = C (or any n large enough that 2^n > C). Use Nat.lt_two_pow_self or similar to get C < 2^C.
-/
theorem erdos_181_minimal_variant_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumberSuperlinear G ≤ C * 2 ^ n) := by
  simp +zetaDelta at *;
  intro C hC;
  use C + 1;
  intro G hG
  simp [GraphRamseyNumberSuperlinear];
  nlinarith [ pow_pos ( zero_lt_two' ℕ ) ( C + 1 ), show 2 ^ ( C + 1 ) > C by exact Nat.recOn C ( by norm_num ) fun n ihn => by norm_num [ Nat.pow_succ ] at * ; linarith ]

end Erdos181