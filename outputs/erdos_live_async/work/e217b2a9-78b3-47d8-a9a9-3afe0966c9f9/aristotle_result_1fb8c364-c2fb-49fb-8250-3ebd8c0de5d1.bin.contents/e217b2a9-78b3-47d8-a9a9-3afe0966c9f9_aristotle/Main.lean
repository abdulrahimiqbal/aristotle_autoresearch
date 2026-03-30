/-
Experiment ID: e217b2a9-78b3-47d8-a9a9-3afe0966c9f9
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
Trivial: pick C = 1. For any n, pick G = ⊥ (the empty graph). IsHypercubeGraph is True, and GraphRamseyNumber is 0 ≤ 1 * 2^n. Use exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩ or similar.
-/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  -- Set $C$ to be $1$.
  use 1
  simp_all +decide [Erdos181.IsHypercubeGraph, Erdos181.GraphRamseyNumber]

end Erdos181

/-!
## Fragility Analysis

### The original theorem is trivially true

The placeholder definitions make the theorem vacuous:
- `IsHypercubeGraph n G := True` means any graph qualifies.
- `GraphRamseyNumber G := 0` means the Ramsey number is always 0.

We prove it below to demonstrate this fragility.
-/

namespace Erdos181.FragilityWitness

/-
PROBLEM
The original theorem is trivially provable because `GraphRamseyNumber` is
identically zero and `IsHypercubeGraph` is identically true. This proof serves
as a **fragility witness**: the formalization imposes no real constraint.

PROVIDED SOLUTION
Same as erdos_181_hypercube_ramsey: pick C = 1, G = ⊥. IsHypercubeGraph unfolds to True, GraphRamseyNumber unfolds to 0. Use exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩.
-/
theorem erdos_181_trivial :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      Erdos181.IsHypercubeGraph n G ∧ Erdos181.GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨ 1, by norm_num, fun n => ⟨ ⊥, trivial, Nat.zero_le _ ⟩ ⟩

end Erdos181.FragilityWitness

/-!
### Falsifying witness for a strengthened (non-trivial) variant

If we replace the placeholder `GraphRamseyNumber` with one that returns a
super-exponential value — say `(2^n)^2` — then no constant `C` can satisfy the
bound `C * 2^n ≥ (2^n)^2 = 2^(2n)` for all `n`. This shows that the linear-in-
`2^n` conclusion is the **most fragile** part of the statement: it depends
entirely on the Ramsey number growing at most linearly in the size of the
hypercube, and any super-linear lower bound breaks it.
-/

namespace Erdos181.Counterexample

/-- A "malicious" Ramsey number that grows as `(2^n)^2 = 2^(2n)`. -/
def BadRamseyNumber (n : ℕ) : ℕ := (2 ^ n) ^ 2

/-
PROBLEM
With the super-exponential `BadRamseyNumber`, the Erdős 181 conclusion fails:
there is **no** constant `C` such that `BadRamseyNumber n ≤ C * 2^n` for all `n`.
This is the falsifying witness for the most fragile variant.

PROVIDED SOLUTION
Unfold BadRamseyNumber to (2^n)^2 = 2^(2n). If ∃ C ≥ 1, ∀ n, 2^(2n) ≤ C * 2^n, then dividing both sides by 2^n gives 2^n ≤ C for all n, which is impossible since 2^n is unbounded. Formally: assume ⟨C, _, hC⟩. Specialize at n = C+1 (or any sufficiently large n). We need (2^n)^2 ≤ C * 2^n, i.e. 2^n * 2^n ≤ C * 2^n. Since 2^n > 0, cancel to get 2^n ≤ C. But 2^n grows without bound, so pick n large enough that 2^n > C. Specifically n = C works since 2^C > C for all C ≥ 1 (or even C ≥ 0 with the right argument).
-/
theorem no_linear_bound_on_bad_ramsey :
    ¬ ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, BadRamseyNumber n ≤ C * 2 ^ n := by
  simp +zetaDelta at *;
  intro x hx
  use x + 1
  generalize_proofs at *; (
  exact Nat.recOn x ( by norm_num [ BadRamseyNumber ] ) fun n ihn => by norm_num [ Nat.pow_succ', BadRamseyNumber ] at * ; nlinarith;)

end Erdos181.Counterexample