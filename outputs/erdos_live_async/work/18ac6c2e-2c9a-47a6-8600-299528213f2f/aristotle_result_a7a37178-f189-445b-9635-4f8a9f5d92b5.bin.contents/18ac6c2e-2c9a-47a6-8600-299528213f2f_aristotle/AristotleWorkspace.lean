/-
Experiment ID: 18ac6c2e-2c9a-47a6-8600-299528213f2f
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "most_fragile_variant"}

# Falsifying witness for the most fragile observed variant

The original Erdős-44-style conjecture (in `Main.lean`) uses the bound `(1-ε)·√M`.
The most fragile observed variant is obtained by replacing `(1-ε)` with `(1+ε)`,
which we call `erdos_44_strengthened`.

We prove `erdos_44_strengthened_false : ¬ erdos_44_strengthened` — the (1+ε) variant
is provably false — by establishing the classical pair-sum counting upper bound for
Sidon sets and showing it contradicts the strengthened density target.

## Proof outline

1. **`sidon_card_sq_le`**: For a Sidon set A ⊆ {1,…,N}, the injective pair-sum map
   on ordered pairs (a,b) with a < b yields |A|² ≤ 4N + |A|.

2. **`sidon_card_lt_three_sqrt_M`**: Combined with the quadratic bound, any Sidon
   set S ⊆ {1,…,M} with M ≥ 1 satisfies |S| < 3·√M.

3. **`erdos_44_strengthened_false`**: Instantiate ε = 2 in the strengthened variant.
   The target becomes |A ∪ B| ≥ 3·√M, which directly contradicts step 2.

This pinpoints the threshold: the constant before √M can be at most ~2 (from the
pair-counting bound), so (1+ε) with ε > 1 is provably impossible, while the original
(1-ε) with ε ∈ (0,1) remains in the feasible range. The (1+ε) variant is the
"most fragile" because it sits just beyond what the combinatorial upper bound permits.
-/

import Mathlib

noncomputable section

namespace Erdos44

open scoped BigOperators

/-- A finite set of natural numbers is Sidon if equal pair sums are trivial up to
reordering of the summands. -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ## Step 1: The pair-sum counting bound -/

/-- Pair-sum counting bound: For a Sidon set A ⊆ {1,...,N}, we have |A|² ≤ 4N + |A|.
The proof maps each ordered pair (a,b) with a < b to a+b; the Sidon property makes
this map injective, and all sums lie in {3,...,2N}. -/
lemma sidon_card_sq_le (A : Finset ℕ) (N : ℕ) (hA : A ⊆ Finset.Icc 1 N)
    (hS : IsSidonFinset A) :
    A.card ^ 2 ≤ 4 * N + A.card := by
  have h_distinct_sums :
      (Finset.image (fun p : ℕ × ℕ => p.1 + p.2)
        (Finset.filter (fun p : ℕ × ℕ => p.1 < p.2) (A ×ˢ A))).card ≤ 2 * N - 2 := by
    have h_subset : Finset.image (fun p : ℕ × ℕ => p.1 + p.2)
        (Finset.filter (fun p : ℕ × ℕ => p.1 < p.2) (A ×ˢ A)) ⊆ Finset.Icc 3 (2 * N) := by
      grind
    exact le_trans (Finset.card_le_card h_subset) (by simp +arith +decide)
  rw [Finset.card_image_of_injOn] at h_distinct_sums
  · have h_pairs :
        (Finset.filter (fun p : ℕ × ℕ => p.1 < p.2) (A ×ˢ A)).card =
        (Finset.powersetCard 2 A).card := by
      refine' Finset.card_bij (fun p _ => {p.1, p.2}) _ _ _
      · grind
      · simp +contextual [Finset.Subset.antisymm_iff, Finset.subset_iff]; lia
      · simp +decide [Finset.mem_powersetCard]
        intro b hb hb'
        rw [Finset.card_eq_two] at hb'
        obtain ⟨a, b, hab, rfl⟩ := hb'
        cases lt_trichotomy a b <;> aesop
    rcases n : Finset.card A with (_ | _ | n) <;>
      simp_all +decide [Nat.choose_two_right]
    lia
  · intro p hp q hq h_eq
    have h_cases : p = q ∨ p = (q.2, q.1) := by aesop
    grind

/-! ## Step 2: From the quadratic bound to |S| < 3√M -/

/-- Any Sidon set S ⊆ {1,...,M} with M ≥ 1 has |S| < 3·√M.
Combines `sidon_card_sq_le` (giving s² ≤ 4M + s) with the elementary
inequality 2·√M + 1 ≤ 3·√M for M ≥ 1. -/
lemma sidon_card_lt_three_sqrt_M (S : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hS_sub : S ⊆ Finset.Icc 1 M) (hS_sidon : IsSidonFinset S) :
    (S.card : ℝ) < 3 * Real.sqrt (M : ℝ) := by
  have := sidon_card_sq_le S M hS_sub hS_sidon
  contrapose! this with h_contra
  rw [← @Nat.cast_lt ℝ]; push_cast
  nlinarith [show 1 ≤ Real.sqrt M by exact Real.le_sqrt_of_sq_le (mod_cast hM),
             Real.mul_self_sqrt (Nat.cast_nonneg M)]

/-! ## Step 3: Falsifying the (1+ε) variant -/

/-- Subset lemma: A ∪ B ⊆ Icc 1 M when A ⊆ Icc 1 N, B ⊆ Icc (N+1) M, N ≤ M. -/
lemma union_subset_Icc {A B : Finset ℕ} {N M : ℕ}
    (hA : A ⊆ Finset.Icc 1 N) (hB : B ⊆ Finset.Icc (N + 1) M) (hNM : N ≤ M) :
    A ∪ B ⊆ Finset.Icc 1 M := by
  grind

/-- The (1+ε) strengthened variant of the Sidon extension conjecture.
Differs from the original conjecture in `Main.lean` only by
replacing `(1 - ε)` with `(1 + ε)`. -/
def erdos_44_strengthened : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N Mε ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            (1 + ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)

/-- **Main result.** The (1+ε)-strengthened Erdős 44 variant is false.

*Falsifying witness:* ε = 2 (so the density target is 3·√M).
For any proposed Mε, take N = max Mε 1 and A = {1}.
For every M ≥ max N Mε and every B with A ∪ B Sidon,
`sidon_card_lt_three_sqrt_M` gives |A ∪ B| < 3·√M,
contradicting the requirement |A ∪ B| ≥ (1+2)·√M = 3·√M. -/
theorem erdos_44_strengthened_false : ¬ erdos_44_strengthened := by
  intro h
  obtain ⟨Mε, hMε⟩ := h 2 (by norm_num)
  obtain ⟨M, hM₁, B, hB₁, hB₂, hB₃⟩ :=
    hMε (Max.max Mε 1) (by norm_num) {1} (by norm_num)
      (by unfold IsSidonFinset; aesop)
  norm_num at *
  have := sidon_card_lt_three_sqrt_M (insert 1 B) M (by linarith) ?_ ?_ <;> norm_num at *
  · linarith
  · exact Finset.insert_subset_iff.mpr
      ⟨Finset.mem_Icc.mpr ⟨by norm_num, by linarith⟩,
       hB₁.trans <| Finset.Icc_subset_Icc (by norm_num) le_rfl⟩
  · assumption

/-!
## Summary

- `erdos_44_strengthened` is the (1+ε) variant of the conjecture from `Main.lean`.
- `erdos_44_strengthened_false` is a machine-verified proof that this variant is **false**.
- The falsifying witness is ε = 2, A = {1}, exploiting the pair-counting upper bound.
- The original (1-ε) conjecture in `Main.lean` remains an open problem
  (it is **not** refuted by the counting argument, since (1-ε) < 1 < 2).
-/

end Erdos44
