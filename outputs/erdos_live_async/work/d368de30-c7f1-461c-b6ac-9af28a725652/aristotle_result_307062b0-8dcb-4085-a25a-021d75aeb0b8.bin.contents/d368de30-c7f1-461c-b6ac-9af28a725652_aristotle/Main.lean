/-
Experiment ID: d368de30-c7f1-461c-b6ac-9af28a725652
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

/-- A self-contained Lean 4 stub for Erdos Problem 181, modeled on the informal
statement used on erdosproblems.com. -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n :=
  ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-!
## Fragility analysis: falsifying witness for the placeholder definitions

The theorem `erdos_181_hypercube_ramsey` is **trivially true** as stated, because:

1. `IsHypercubeGraph n G` is defined as `True`, so every graph vacuously satisfies it.
2. `GraphRamseyNumber G` is defined as `0`, so the Ramsey bound `0 ≤ C * 2^n` holds for
   any `C ≥ 1`.

The proof is literally `⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩` — no
mathematical content whatsoever. The placeholders completely decouple the formal statement
from the intended mathematical claim (Erdős Problem 181).

### Independence-style witness

Below we demonstrate that the theorem remains provable even with *any* predicate for
`IsHypercubeGraph`, as long as `GraphRamseyNumber` stays at `0`. We also show that
swapping `GraphRamseyNumber` to any non-trivial function (e.g., returning `2^(2^n)`)
while keeping `IsHypercubeGraph := True` makes the statement **false** for large `n`.
-/

/-- Witness 1: The theorem is provable for **any** `IsHypercubeGraph` predicate
whatsoever, as long as `GraphRamseyNumber = 0`. This shows the Ramsey-number
placeholder alone makes the statement vacuous. -/
theorem fragility_witness_ramsey_zero
    (P : ∀ n : ℕ, SimpleGraph (Fin (2 ^ n)) → Prop)
    (hP : ∀ n, ∃ G : SimpleGraph (Fin (2 ^ n)), P n G) :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      P n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨1, le_refl 1, fun n => let ⟨G, hG⟩ := hP n; ⟨G, hG, Nat.zero_le _⟩⟩

/-- Witness 2: If `IsHypercubeGraph := True` but `GraphRamseyNumber` returns
something super-exponential (e.g. `2^(2^n)`), the statement becomes **false**
for large enough `n`. This is the most fragile observed variant — it breaks the
moment the Ramsey-number placeholder is replaced by anything non-trivial.

Concretely, we define `BigRamsey G := 2^(2^n)` and show the negation of the
analogous statement: no constant `C` can bound `2^(2^n)` by `C * 2^n` for all `n`. -/
def BigRamsey (n : ℕ) (_G : SimpleGraph (Fin (2 ^ n))) : ℕ :=
  2 ^ (2 ^ n)

theorem fragility_witness_superexp_ramsey :
    ¬ ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ BigRamsey n G ≤ C * 2 ^ n := by
  simp +zetaDelta at *;
  intro C hC;
  -- Choose $n$ such that $2^{2^n} > C * 2^n$.
  obtain ⟨n, hn⟩ : ∃ n, 2 ^ (2 ^ n) > C * 2 ^ n := by
    use C + 1;
    induction' hC with k hk ih <;> norm_num [ Nat.pow_succ, Nat.pow_mul ] at *;
    nlinarith [ Nat.mul_le_mul_left ( 2 ^ k ) hk, Nat.pow_le_pow_right ( by decide : 1 ≤ 2 ) ( show k ≥ 1 by linarith ), Nat.pow_le_pow_right ( by decide : 1 ≤ 2 ) ( show 2 ^ k ≥ k + 1 by exact Nat.recOn k ( by norm_num ) fun n ihn => by rw [ pow_succ' ] ; nlinarith [ Nat.pow_le_pow_right ( by decide : 1 ≤ 2 ) ihn ] ) ];
  exact ⟨ n, fun _ _ => hn ⟩

end Erdos181