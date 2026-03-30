/-
Experiment ID: 3f052870-3562-4062-abf7-7950d9446de0
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

/-- The original statement is trivially true because `IsHypercubeGraph` is `True`
and `GraphRamseyNumber` is `0`. This proof witnesses the fragility: the statement
holds vacuously, independent of any real Ramsey-theoretic content. -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n := by
  exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

/-! ## Fragile variant: superlinear Ramsey lower bound

The "most fragile" variant is obtained by replacing `GraphRamseyNumber` with
any definition that grows faster than `O(2^n)` in the number of vertices.
Below we use `|V(G)|² = (2^n)² = 2^{2n}`, which grows superexponentially
relative to `2^n`. With this substitution, no constant `C` can satisfy
`R(G) ≤ C · 2^n` for all `n`, giving a clean falsifying witness. -/

/-- Non-trivial "Ramsey number" placeholder: returns |V(G)|², i.e. `(2^n)²`.
This models any Ramsey-type quantity that grows faster than linearly in `|V|`. -/
def GraphRamseyNumber_strong {α : Type*} [Fintype α] (G : SimpleGraph α) : ℕ :=
  (Fintype.card α) ^ 2

/-
PROBLEM
**Falsifying witness**: no constant `C` can bound `(2^n)²` by `C · 2^n` for
all `n`. This disproves the "strengthened" variant and shows the original
formalization is fragile — it holds only because the Ramsey number placeholder
is trivially zero.

PROVIDED SOLUTION
Assume ⟨C, hC1, hC⟩. Specialize at n = C+1. Get G with (2^(C+1))^2 ≤ C * 2^(C+1). Since 2^(C+1) > 0, this gives 2^(C+1) ≤ C. But two_pow_succ_gt says C < 2^(C+1). Contradiction by omega.
-/
theorem erdos_181_strong_variant_false :
    ¬ (∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber_strong G ≤ C * 2 ^ n) := by
  -- Assume for contradiction that there exists a constant `C` such that `GraphRamseyNumber_strong G ≤ C * 2^n` for all `n`.
  by_contra h_contra

  obtain ⟨C, hC_pos, hC⟩ := h_contra
  have hC_ge_one : 1 ≤ C := by
    assumption

  -- Fix any `n`. We need to find a `G` such that `IsHypercubeGraph n G` and `GraphRamseyNumber_strong G ≤ C * 2^n`.
  have h_exists_G : ∃ G : SimpleGraph (Fin (2 ^ (C + 1))), IsHypercubeGraph (C + 1) G ∧ GraphRamseyNumber_strong G ≤ C * 2 ^ (C + 1) := by
    exact hC _;
  obtain ⟨ G, hG₁, hG₂ ⟩ := h_exists_G; have := hG₂; simp_all +decide [ GraphRamseyNumber_strong ] ;
  have := hC ( C + 1 ) ; norm_num [ pow_succ' ] at this;
  linarith [ Nat.pow_le_pow_right ( by decide : 1 ≤ 2 ) hC_ge_one, show 2 ^ C > C from Nat.recOn C ( by norm_num ) fun n ihn => by rw [ pow_succ' ] ; linarith [ Nat.pow_le_pow_right ( by decide : 1 ≤ 2 ) n.zero_le ] ]

/-
PROBLEM
Helper: `2^(n+1) > n` for all `n`.

PROVIDED SOLUTION
Induction on n. Base: 0 < 2. Step: if n < 2^(n+1) then n+1 < 2^(n+1) ≤ 2*2^(n+1) = 2^(n+2).
-/
lemma two_pow_succ_gt (n : ℕ) : n < 2 ^ (n + 1) := by
  exact Nat.recOn n ( by norm_num ) fun n ih => by norm_num [ Nat.pow_succ' ] at * ; linarith;

end Erdos181