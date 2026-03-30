/-
Experiment ID: b607963b-2408-45f0-8e80-7c5127d84ef7
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "most_fragile_variant"}
-/

-- counterexample mode target
import Mathlib

noncomputable section

namespace Erdos44

open scoped BigOperators
open Finset

/-- A finite set of natural numbers is Sidon if equal pair sums are trivial up to
reordering of the summands. -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-- A workspace-local Lean 4 stub for Erdős Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape. -/
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
## Counterexample to the most fragile observed variant

The original theorem uses the lower bound `(1 - ε) * √M`.  The theoretical maximum
size of a Sidon set in `[1, M]` is governed by the **counting bound**: distinct
positive differences force `|A| * (|A| - 1) / 2 ≤ M - 1`, yielding
`|A| ≤ (1 + √(8M - 7)) / 2 ∼ √(2M)`.

The **most fragile variant** replaces `(1 - ε) * √M` with `(√2 + ε) * √M`, attempting
to push the density past the counting bound ceiling of `√(2M)`.  We exhibit a concrete
counterexample showing this variant is **false**: for any purported threshold `Mε`, we
can choose `N` large enough and `A = {1}` so that every `M ≥ N` violates the counting
bound.
-/

section CountingBound

/-- **Sidon counting bound (difference form).**
For a Sidon set `A ⊆ Finset.Icc 1 M`, the map `(a, b) ↦ a - b` on ordered pairs
with `a > b` is injective, and the image lands in `Finset.Icc 1 (M - 1)`.
Hence `A.card * (A.card - 1) / 2 ≤ M - 1`. -/
theorem sidon_card_bound (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    A.card * (A.card - 1) / 2 ≤ M - 1 := by
  set D := Finset.image (fun (p : ℕ × ℕ) => p.1 - p.2) (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A)) with hD_def;
  have hD_subset : D ⊆ Finset.Icc 1 (M - 1) := by
    exact Finset.image_subset_iff.mpr fun p hp => Finset.mem_Icc.mpr ⟨ Nat.sub_pos_of_lt <| Finset.mem_filter.mp hp |>.2, Nat.sub_le_sub_right ( Finset.mem_Icc.mp ( hA <| Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.1 ) |>.2 ) _ |> le_trans <| Nat.sub_le_sub_left ( Finset.mem_Icc.mp ( hA <| Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.2 ) |>.1 ) _ ⟩;
  have hD_card : D.card = A.card * (A.card - 1) / 2 := by
    have h_pairs : (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A)).card = Finset.card (Finset.powersetCard 2 A) := by
      refine' Finset.card_bij ( fun p hp => { p.1, p.2 } ) _ _ _;
      · grind;
      · simp +contextual [ Finset.Subset.antisymm_iff, Finset.subset_iff ];
        intros; omega;
      · simp +zetaDelta at *;
        intro b hb hb'; rw [ Finset.card_eq_two ] at hb'; obtain ⟨ a, b, hab, rfl ⟩ := hb'; cases lt_trichotomy a b <;> aesop;;
    rw [ Finset.card_image_of_injOn, h_pairs ];
    · rw [ Finset.card_powersetCard, Nat.choose_two_right ];
    · intros p hp q hq h_eq
      have h_eq' : p.1 + q.2 = q.1 + p.2 := by
        grind;
      have := hS ( Finset.mem_filter.mp hp |>.1 |> Finset.mem_product.mp |>.1 ) ( Finset.mem_filter.mp hq |>.1 |> Finset.mem_product.mp |>.2 ) ( Finset.mem_filter.mp hq |>.1 |> Finset.mem_product.mp |>.1 ) ( Finset.mem_filter.mp hp |>.1 |> Finset.mem_product.mp |>.2 ) ; aesop;
  have hD_card_le_M_minus_1 : D.card ≤ M - 1 := by
    exact le_trans ( Finset.card_le_card hD_subset ) ( by simpa )
  linarith [Nat.div_mul_cancel ( show 2 ∣ A.card * ( A.card - 1 ) from even_iff_two_dvd.mp ( Nat.even_mul_pred_self _ ) )]

/-- The real-valued corollary: `(A.card : ℝ) ^ 2 - A.card ≤ 2 * M - 2` for Sidon
sets, which implies `(A.card : ℝ) ≤ (1 + Real.sqrt (8 * M - 7)) / 2`. -/
theorem sidon_card_sq_sub_card_le (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    (A.card : ℝ) ^ 2 - A.card ≤ 2 * M - 2 := by
  have h_count : A.card * (A.card - 1) ≤ 2 * M - 2 := by
    convert Nat.mul_le_mul_left 2 ( sidon_card_bound A M hM hA hS ) using 1 ; ring;
    · rw [ Nat.div_mul_cancel ( even_iff_two_dvd.mp ( Nat.even_mul_pred_self _ ) ) ];
    · rw [ Nat.mul_sub_left_distrib, Nat.mul_one ];
  rcases x : Finset.card A with ( _ | _ | k ) <;> simp_all +decide [ Nat.mul_succ, sq ];
  rw [ le_tsub_iff_left ] at h_count <;> try linarith;
  linarith [ ( by norm_cast : ( 2 : ℝ ) + ( ( k + 1 + 1 ) * k + ( k + 1 + 1 ) ) ≤ 2 * M ) ]

/-
PROBLEM
For any `δ > 0`, there exists `M₀` such that for all `M ≥ M₀` and all Sidon sets
`A ⊆ [1, M]`, `A.card < (√2 + δ) * √M`.  This follows from the counting bound
`k² - k ≤ 2M - 2`, which for large `M` prevents `k ≥ (√2 + δ)√M`.

PROVIDED SOLUTION
From sidon_card_sq_sub_card_le, for any Sidon A ⊆ [1,M]: k² - k ≤ 2M - 2 where k = A.card.

By contradiction, suppose k ≥ (√2+δ)√M. Then k² ≥ (√2+δ)²·M = (2+2δ√2+δ²)·M.
Also k ≤ (√2+δ)√M + something, but we can use k ≥ 0.
From k² - k ≤ 2M - 2 and k² ≥ (2+2δ√2+δ²)M:
(2+2δ√2+δ²)M - k ≤ 2M - 2
So k ≥ (2δ√2+δ²)M + 2.
But also k ≥ (√2+δ)√M, and (√2+δ)√M ≥ (2δ√2+δ²)M + 2 requires √M ≤ something bounded.

More precisely: k ≥ (√2+δ)√M and k² - k ≤ 2M-2 imply:
(√2+δ)²M - (√2+δ)√M ≤ k² - k ≤ 2M - 2
(2δ√2+δ²)M ≤ (√2+δ)√M - 2
(2δ√2+δ²)√M ≤ (√2+δ) - 2/√M < √2+δ
√M < (√2+δ)/(2δ√2+δ²)
M < ((√2+δ)/(2δ√2+δ²))²

So choose M₀ = ⌈((√2+δ)/(2δ√2+δ²))²⌉ + 1. For M ≥ M₀, we get contradiction.

Use Archimedean property to get M₀. The proof is by contraposition: assume k ≥ (√2+δ)√M, use sidon_card_sq_sub_card_le to get k²-k ≤ 2M-2, then derive √M < C for some constant C, contradicting M ≥ M₀ for large enough M₀.
-/
theorem sidon_eventually_below_sqrt2_plus_eps (δ : ℝ) (hδ : δ > 0) :
    ∃ M₀ : ℕ, ∀ M : ℕ, M₀ ≤ M →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 M → IsSidonFinset A →
        (A.card : ℝ) < (Real.sqrt 2 + δ) * Real.sqrt (M : ℝ) := by
  -- Let $k = A.card$ and assume $k \geq (\sqrt{2} + \delta) \sqrt{M}$.
  suffices h_contra : ∀ {M : ℕ}, 1 ≤ M → ∀ A : Finset ℕ,
    A ⊆ Finset.Icc 1 M →
      IsSidonFinset A →
        (A.card : ℝ) ≥ (Real.sqrt 2 + δ) * Real.sqrt M →
          (Real.sqrt M) < (Real.sqrt 2 + δ) / (2 * δ * Real.sqrt 2 + δ ^ 2) by
            -- Choose $M₀$ such that for all $M ≥ M₀$, $\sqrt{M} > \frac{\sqrt{2} + δ}{2δ \sqrt{2} + δ^2}$.
            obtain ⟨M₀, hM₀⟩ : ∃ M₀ : ℕ, ∀ M : ℕ, M₀ ≤ M → Real.sqrt M > (Real.sqrt 2 + δ) / (2 * δ * Real.sqrt 2 + δ ^ 2) := by
              exact ⟨ ⌊ ( ( Real.sqrt 2 + δ ) / ( 2 * δ * Real.sqrt 2 + δ ^ 2 ) ) ^ 2⌋₊ + 1, fun M hM => Real.lt_sqrt_of_sq_lt <| Nat.lt_of_floor_lt hM ⟩
            generalize_proofs at *;
            exact ⟨ M₀ + 1, fun M hM A hA hA' => not_le.1 fun h => not_le_of_gt ( hM₀ M ( by linarith ) ) ( le_of_lt ( h_contra ( by linarith ) A hA hA' h ) ) ⟩
  generalize_proofs at *;
  intro M hM A hA hS hA_ge
  have h_ineq : (Real.sqrt 2 + δ) ^ 2 * M - (Real.sqrt 2 + δ) * Real.sqrt M ≤ 2 * M - 2 := by
    have h_ineq : (A.card : ℝ) ^ 2 - A.card ≤ 2 * M - 2 := by
      convert sidon_card_sq_sub_card_le A M hM hA hS using 1
    generalize_proofs at *; (
    refine le_trans ?_ h_ineq
    generalize_proofs at *; (
    nlinarith only [ show 0 ≤ ( Real.sqrt 2 + δ ) * Real.sqrt M by positivity, hA_ge, show ( A.card : ℝ ) ≥ 1 by exact_mod_cast Finset.card_pos.mpr <| Finset.nonempty_of_ne_empty <| by rintro rfl; exact absurd hA_ge <| by norm_num; positivity, Real.mul_self_sqrt <| Nat.cast_nonneg M ]))
  generalize_proofs at *; (
  rw [ lt_div_iff₀ ] <;> nlinarith [ show 0 < 2 * δ * Real.sqrt 2 + δ ^ 2 by positivity, Real.sqrt_nonneg 2, Real.sq_sqrt zero_le_two, Real.sqrt_nonneg M, Real.sq_sqrt <| Nat.cast_nonneg M ] ;);

end CountingBound

section FragileVariant

/-- The **most fragile variant**: strengthens the density bound from
`(1 - ε) * √M` to `(Real.sqrt 2 + ε) * √M ≈ √(2M) + ε√M`.

This exceeds the counting-bound ceiling for large `M`, making the statement false. -/
def fragile_variant : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N Mε ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            (Real.sqrt 2 + ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)

/-- The singleton `{1}` is always Sidon. -/
theorem singleton_one_sidon : IsSidonFinset {1} := by
  unfold IsSidonFinset; aesop;

/-
PROBLEM
`{1} ⊆ Finset.Icc 1 N` for any `N ≥ 1`.

PROVIDED SOLUTION
1 ∈ Finset.Icc 1 N since 1 ≤ 1 ≤ N. Use Finset.singleton_subset_iff and Finset.mem_Icc.
-/
theorem singleton_one_subset_Icc (N : ℕ) (hN : 1 ≤ N) : ({1} : Finset ℕ) ⊆ Finset.Icc 1 N := by
  aesop

/-
PROBLEM
If `A ∪ B ⊆ Finset.Icc 1 M` whenever `A ⊆ Finset.Icc 1 N` and
`B ⊆ Finset.Icc (N+1) M`.

PROVIDED SOLUTION
Every element of A is in [1,N] ⊆ [1,M] (since N ≤ M), and every element of B is in [N+1,M] ⊆ [1,M]. So A ∪ B ⊆ [1,M]. Use Finset.union_subset and Finset.Icc_subset_Icc.
-/
theorem union_subset_Icc (A B : Finset ℕ) (N M : ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hB : B ⊆ Finset.Icc (N + 1) M) (hNM : N ≤ M) :
    A ∪ B ⊆ Finset.Icc 1 M := by
  exact Finset.union_subset ( Finset.Subset.trans hA ( Finset.Icc_subset_Icc_right hNM ) ) ( Finset.Subset.trans hB ( Finset.Icc_subset_Icc_left ( by linarith ) ) )

/-
PROBLEM
**Main result: the fragile variant is false.**

Proof sketch: Fix `ε > 0`. Obtain `M₀` from `sidon_eventually_below_sqrt2_plus_eps`.
Given any purported `Mε`, take `N = max Mε M₀ + 1` and `A = {1}`.
For any `M ≥ max N Mε ≥ M₀` and any `B ⊆ [N+1, M]`, the set `A ∪ B` is a subset of
`[1, M]`. If `A ∪ B` is Sidon, then `|A ∪ B| < (√2 + ε)√M` by the counting bound,
contradicting the fragile variant's requirement `(√2 + ε)√M ≤ |A ∪ B|`.

PROVIDED SOLUTION
Unfold fragile_variant. Assume for contradiction that it holds. Instantiate with ε = 1 (any ε > 0 works). Get Mε. From sidon_eventually_below_sqrt2_plus_eps with δ = 1, get M₀ such that for M ≥ M₀ and any Sidon A ⊆ [1,M], A.card < (√2+1)√M.

Choose N = max Mε M₀ + 1. Then N ≥ 1. Take A = {1} which is Sidon (singleton_one_sidon) and {1} ⊆ Finset.Icc 1 N (singleton_one_subset_Icc).

The fragile variant gives us M ≥ max N Mε, and B ⊆ Finset.Icc (N+1) M with IsSidonFinset (A ∪ B) and (√2+1)√M ≤ |A ∪ B|.

Since M ≥ N ≥ M₀ + 1 > M₀, and A ∪ B ⊆ Finset.Icc 1 M (by union_subset_Icc, since A ⊆ [1,N] and B ⊆ [N+1,M] and N ≤ M), and A ∪ B is Sidon, we get |A ∪ B| < (√2+1)√M from sidon_eventually_below_sqrt2_plus_eps.

But the fragile variant says (√2+1)√M ≤ |A ∪ B|. Contradiction: |A ∪ B| < (√2+1)√M and (√2+1)√M ≤ |A ∪ B|.
-/
theorem fragile_variant_false : ¬ fragile_variant := by
  intro h
  obtain ⟨Mε, hMε⟩ := h 1 zero_lt_one;
  -- Apply the fragile variant with `N = max Mε M₀ + 1` and `A = {1}`.
  obtain ⟨ M₀, hM₀ ⟩ := sidon_eventually_below_sqrt2_plus_eps 1 one_pos;
  obtain ⟨ M, hM_ge, B, hB, hSidon, hBound ⟩ := hMε (max Mε M₀ + 1) (by omega) {1} (singleton_one_subset_Icc _ (by omega)) singleton_one_sidon;
  have hM_ge_M₀ : M₀ ≤ M := by
    linarith [ Nat.le_max_left Mε M₀, Nat.le_max_right Mε M₀, Nat.le_max_left ( max Mε M₀ + 1 ) Mε, Nat.le_max_right ( max Mε M₀ + 1 ) Mε ];
  have hAB_sub : ({1} ∪ B : Finset ℕ) ⊆ Finset.Icc 1 M := by
    grind;
  have hlt := hM₀ M hM_ge_M₀ ({1} ∪ B) hAB_sub hSidon;
  linarith;

end FragileVariant

end Erdos44