/-
Experiment ID: 64e5dfe2-bcdb-4af1-b66d-1b32da12b543
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 22, "target": "boundary_variant"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
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

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

NOTE: This is an open problem in additive combinatorics. The statement asserts that any
Sidon set can be extended to achieve density (1 - ε)/√M for arbitrarily large M.
Proving this formally would require deep results about Sidon set constructions
(Erdős–Turán, Singer difference sets) and extension theorems. We leave it as sorry. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

/-!
## Boundary variant and counterexample

The **boundary variant** replaces the factor `(1 - ε)` with `(1 + ε)`, asking whether
a Sidon set can be extended to achieve *super-√M* density. This is **FALSE**: the classical
counting bound shows every Sidon set in `[1, M]` has fewer than `2√M` elements, so the
`(1 + ε)` variant fails for `ε ≥ 1`.

### Proof strategy

1. **`sidon_diff_injective`**: Distinct pairs in a Sidon set yield distinct differences.
2. **`sidon_pairs_bound`**: The number of ordered pairs `|A|·(|A|-1)` is at most `2·(M-1)`,
   by injecting the `C(|A|,2)` differences into `{1,…,M-1}`.
3. **`sidon_card_lt_two_sqrt`**: From the counting bound, any Sidon subset of `[1,M]` has
   strictly fewer than `2√M` elements.
4. **`erdos_44_boundary_variant_false`**: Instantiate `ε = 1` and `A = ∅`. For any `M ≥ 1`,
   every Sidon `B ⊆ [1,M]` satisfies `|B| < 2√M`, contradicting `2√M ≤ |B|`.
-/

/-- The empty set is Sidon (vacuously). -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  tauto

/-- A subset of a Sidon set is Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (hB : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A := by
  exact fun a b c d ha hb hc hd h => hB (hAB ha) (hAB hb) (hAB hc) (hAB hd) h

/-- Distinct pairs in a Sidon set have distinct differences. That is, if
`a < b` and `c < d` are two pairs in a Sidon set with `b - a = d - c`,
then `a = c` and `b = d`. -/
lemma sidon_diff_injective (A : Finset ℕ) (hS : IsSidonFinset A)
    (a b c d : ℕ) (ha : a ∈ A) (hb : b ∈ A) (hc : c ∈ A) (hd : d ∈ A)
    (hab : a < b) (hcd : c < d) (heq : b - a = d - c) : a = c ∧ b = d := by
  grind +locals

/-- Core counting bound: `|A| * (|A| - 1) ≤ 2 * (M - 1)` for any Sidon set `A ⊆ [1, M]`.
The proof injects the `C(|A|, 2)` pairwise differences into `{1, …, M-1}`. -/
lemma sidon_pairs_bound (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    A.card * (A.card - 1) ≤ 2 * (M - 1) := by
  set S := (A ×ˢ A).filter (fun p => p.1 < p.2) with hS_def
  have hS_card : S.card = A.card * (A.card - 1) / 2 := by
    have hS_card : S.card = Finset.card (Finset.powersetCard 2 A) := by
      refine' Finset.card_bij (fun p hp => {p.1, p.2}) _ _ _ <;> simp_all +decide
      · grind
      · simp +contextual [Finset.Subset.antisymm_iff, Finset.subset_iff]
        intros; omega
      · intro b hb hb'
        rw [Finset.card_eq_two] at hb'
        obtain ⟨a, b, hab, rfl⟩ := hb'
        cases lt_trichotomy a b <;> aesop
    rw [hS_card, Finset.card_powersetCard, Nat.choose_two_right]
  have h_inj : Finset.card (Finset.image (fun p : ℕ × ℕ => p.2 - p.1) S) = S.card := by
    rw [Finset.card_image_of_injOn]
    intro p hp q hq
    have := @sidon_diff_injective A hS p.1 p.2 q.1 q.2
    aesop
  have h_image : Finset.image (fun p : ℕ × ℕ => p.2 - p.1) S ⊆ Finset.Icc 1 (M - 1) := by
    exact Finset.image_subset_iff.mpr fun p hp =>
      Finset.mem_Icc.mpr
        ⟨Nat.sub_pos_of_lt <| Finset.mem_filter.mp hp |>.2,
         Nat.sub_le_sub_right
           (Finset.mem_Icc.mp (hA <| Finset.mem_product.mp (Finset.mem_filter.mp hp |>.1) |>.2) |>.2) _ |>
           le_trans <|
             Nat.sub_le_sub_left
               (Finset.mem_Icc.mp (hA <| Finset.mem_product.mp (Finset.mem_filter.mp hp |>.1) |>.1) |>.1) _⟩
  have := Finset.card_mono h_image
  simp_all +decide
  linarith [Nat.div_mul_cancel
    (show 2 ∣ A.card * (A.card - 1) from even_iff_two_dvd.mp (Nat.even_mul_pred_self _))]

/-- Upper bound on Sidon set size: any Sidon set in `[1, M]` has fewer than `2√M` elements.
Derived from `sidon_pairs_bound` by contradiction. -/
lemma sidon_card_lt_two_sqrt (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    (A.card : ℝ) < 2 * Real.sqrt (↑M) := by
  by_contra h_contra
  have h_ge : (A.card : ℝ) ≥ 2 * Real.sqrt M :=
    le_of_not_gt h_contra
  have h_ge_sq : (A.card : ℝ) ^ 2 ≥ 4 * M := by
    nlinarith [Real.sqrt_nonneg M, Real.sq_sqrt (Nat.cast_nonneg M)]
  have := sidon_pairs_bound A M hM hA hS
  norm_cast at *
  nlinarith [Nat.sub_add_cancel (show 1 ≤ A.card from
    Finset.card_pos.mpr <| Finset.nonempty_of_ne_empty <| by
      rintro rfl; norm_num at *; linarith [Real.sqrt_pos.mpr <| Nat.cast_pos.mpr hM]),
    Nat.sub_add_cancel hM]

/-- The boundary variant with `(1 + ε)` in place of `(1 - ε)` is false.
Counterexample: take `ε = 1`. Then `(1 + ε)√M = 2√M`, but every Sidon set in `[1, M]`
has strictly fewer than `2√M` elements by `sidon_card_lt_two_sqrt`. -/
theorem erdos_44_boundary_variant_false :
    ¬ (∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 + ε) * Real.sqrt (↑M) ≤ ((A ∪ B).card : ℝ)) := by
  push_neg
  use 1, one_pos
  intro Mε
  use 1
  simp
  refine Or.inl ⟨isSidonFinset_empty, fun M hM₁ hM₂ B hB₁ hB₂ => ?_⟩
  have := sidon_card_lt_two_sqrt B M hM₁
    (Finset.Subset.trans hB₁ (Finset.Icc_subset_Icc (by norm_num) le_rfl)) hB₂
  norm_num at *
  linarith

#print axioms erdos_44_boundary_variant_false

end Erdos44
