/-
Experiment ID: ba924c59-d41c-4956-86ce-7242a3e484e8
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 18, "target": "minimal_variant"}
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

/-- A workspace-local Lean 4 stub for Erdos Problem 44. This is an **open problem**
in additive combinatorics: it asserts that any Sidon set in `{1, …, N}` can be
extended to a near-optimal Sidon set in a larger interval `{1, …, M}`. -/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry -- Open problem (Erdős Problem 44)

/-!
## Minimal Variant: Strengthened Exponent

The minimal variant replaces the `√M` growth (exponent `1/2`) with `M ^ (3/4)`
(exponent `3/4`). This is the most natural "next step" strengthening of the
original conjecture's density requirement.

**Why this is false**: The classical counting argument shows that any Sidon set
`A ⊆ {1, …, N}` satisfies `|A|(|A| + 1)/2 ≤ 2N − 1` (since the pair-sum map
is injective and all sums lie in `{2, …, 2N}`), giving `|A| < 2√N`. For
`N ≥ 256`, `2√N < N^(3/4)`, so no Sidon set can achieve the `M^(3/4)` density.
This shows the `√M` exponent in the original conjecture is essentially tight.
-/

/-- Minimal variant of Erdős Problem 44: same as `erdos_44_sidon_extension` but with
the density bound strengthened from `(1 - ε) * √M` to `M ^ (3/4)`. -/
def erdos_44_minimal_variant : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ max N Mε ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            (M : ℝ) ^ (3 / 4 : ℝ) ≤ ((A ∪ B).card : ℝ)

/-!
### Sidon Counting Bound

The key tool for disproving the minimal variant is the standard counting
argument: the multiset-pair-sum map `{a, b} ↦ a + b` on a Sidon set `A` is
injective, and all sums lie in `{2, …, 2N}`, giving a quadratic upper bound
on `|A|`.
-/

/-- The pair-sum counting bound for Sidon sets: if `A ⊆ {1, …, N}` is Sidon,
then `|A| * (|A| + 1) ≤ 4N`. This follows from injectivity of the pair-sum map
on `|A|(|A|+1)/2` ordered pairs, with sums in `{2, …, 2N}`. -/
theorem sidon_card_bound (A : Finset ℕ) (N : ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) (hN : 1 ≤ N) :
    A.card * (A.card + 1) ≤ 4 * N := by
  have hB_card : (Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A))).card = A.card * (A.card + 1) / 2 := by
    rw [ Finset.card_image_of_injOn ];
    · have h_comb : (Finset.filter (fun p => p.1 ≤ p.2) (A ×ˢ A)).card = Finset.card (Finset.powersetCard 2 A) + Finset.card A := by
        have h_comb : (Finset.filter (fun p => p.1 ≤ p.2) (A ×ˢ A)).card = Finset.card (Finset.filter (fun p => p.1 < p.2) (A ×ˢ A)) + Finset.card (Finset.filter (fun p => p.1 = p.2) (A ×ˢ A)) := by
          rw [ ← Finset.card_union_of_disjoint ];
          · congr with p ; simp +decide [ le_iff_lt_or_eq ];
            grind;
          · exact Finset.disjoint_filter.mpr fun _ _ _ _ => by linarith;
        have h_comb : (Finset.filter (fun p => p.1 < p.2) (A ×ˢ A)).card = Finset.card (Finset.powersetCard 2 A) := by
          refine' Finset.card_bij ( fun p hp => { p.1, p.2 } ) _ _ _;
          · grind;
          · simp +contextual [ Finset.Subset.antisymm_iff, Finset.subset_iff ];
            intros; omega;
          · intro b hb; rw [ Finset.mem_powersetCard ] at hb; obtain ⟨ x, y, hxy ⟩ := Finset.card_eq_two.mp hb.2; cases lt_trichotomy x y <;> aesop;
        simp_all +decide;
        rw [ show { p ∈ A ×ˢ A | p.1 = p.2 } = Finset.image ( fun x => ( x, x ) ) A by ext ⟨ x, y ⟩ ; aesop, Finset.card_image_of_injective _ fun x y hxy => by injection hxy ];
      rw [ h_comb, Finset.card_powersetCard ];
      exact Eq.symm ( Nat.div_eq_of_eq_mul_left zero_lt_two ( by induction A.card <;> simp +decide [ Nat.choose ] at * ; linarith ) );
    · intros p hp q hq h_eq;
      cases hS ( Finset.mem_filter.mp hp |>.1 |> Finset.mem_product.mp |>.1 ) ( Finset.mem_filter.mp hp |>.1 |> Finset.mem_product.mp |>.2 ) ( Finset.mem_filter.mp hq |>.1 |> Finset.mem_product.mp |>.1 ) ( Finset.mem_filter.mp hq |>.1 |> Finset.mem_product.mp |>.2 ) h_eq ; aesop;
      grind;
  have hB_subset : Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A)) ⊆ Finset.Icc 2 (2 * N) := by
    exact Finset.image_subset_iff.mpr fun p hp => Finset.mem_Icc.mpr ⟨ by linarith [ Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.1 ) ), Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.2 ) ) ], by linarith [ Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.1 ) ), Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.2 ) ) ] ⟩;
  have := Finset.card_le_card hB_subset; simp_all +arith +decide;
  lia

/-- Corollary: for any Sidon set `A ⊆ {1, …, N}`, `|A|² ≤ 4N`. -/
theorem sidon_card_sq_le (A : Finset ℕ) (N : ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) (hN : 1 ≤ N) :
    A.card ^ 2 ≤ 4 * N := by
  linarith [ sidon_card_bound A N hA hS hN ]

/-- `{1}` is a Sidon set. -/
theorem isSidonFinset_singleton : IsSidonFinset {1} := by
  aesop_cat

/-- `{1}` is contained in `Finset.Icc 1 N` for any `N ≥ 1`. -/
theorem singleton_subset_Icc (N : ℕ) (hN : 1 ≤ N) :
    ({1} : Finset ℕ) ⊆ Finset.Icc 1 N := by
  aesop

/-- Any Sidon subset of `Finset.Icc 1 M` that is a union `A ∪ B` also satisfies
the Sidon counting bound. -/
theorem sidon_union_card_sq_le (A B : Finset ℕ) (M : ℕ)
    (hAB : (A ∪ B) ⊆ Finset.Icc 1 M) (hS : IsSidonFinset (A ∪ B)) (hM : 1 ≤ M) :
    (A ∪ B).card ^ 2 ≤ 4 * M :=
  sidon_card_sq_le (A ∪ B) M hAB hS hM

/-- For `M ≥ 256`, we have `2 * √M < M ^ (3/4)`. This is the key inequality
showing that the Sidon upper bound `2√M` falls below the `M^(3/4)` threshold. -/
theorem sqrt_lt_rpow_three_fourths (M : ℕ) (hM : 256 ≤ M) :
    2 * Real.sqrt (M : ℝ) < (M : ℝ) ^ (3 / 4 : ℝ) := by
  rw [ Real.sqrt_eq_rpow ];
  rw [ show ( 3 / 4 : ℝ ) = 1 / 2 + 1 / 4 by norm_num, Real.rpow_add ] <;> norm_num;
  · rw [ mul_comm ] ; gcongr;
    exact lt_of_le_of_lt ( by norm_num ) ( Real.rpow_lt_rpow ( by positivity ) ( Nat.cast_lt.mpr ( show M > 2 ^ 4 by linarith ) ) ( by norm_num ) );
  · grind

/-- **Counterexample**: The minimal variant is false. No Sidon set in `{1, …, M}` can
have `M^(3/4)` elements, because the Sidon counting bound gives `|A| ≤ 2√M < M^(3/4)`
for large `M`. Concretely, we take `A = {1}`, `N = 256 + Mε`, and observe that for
any `M ≥ max(N, Mε) ≥ 256`, any Sidon extension `A ∪ B ⊆ {1,…,M}` satisfies
`|A ∪ B|² ≤ 4M`, hence `|A ∪ B| ≤ 2√M < M^(3/4)`. -/
theorem erdos_44_minimal_variant_false : ¬ erdos_44_minimal_variant := by
  unfold erdos_44_minimal_variant;
  push_neg;
  refine' ⟨ 1, zero_lt_one, fun Mε => _ ⟩;
  refine' ⟨ 256 + Mε, _, { 1 }, _, _, _ ⟩ <;> norm_num;
  · linarith;
  · linarith;
  · exact isSidonFinset_singleton;
  · intro M hM B hB hSidon
    have h_card : (insert 1 B).card ^ 2 ≤ 4 * M := by
      apply sidon_card_sq_le;
      · exact Finset.insert_subset_iff.mpr ⟨ Finset.mem_Icc.mpr ⟨ by linarith, by linarith ⟩, hB.trans <| Finset.Icc_subset_Icc ( by linarith ) le_rfl ⟩;
      · assumption;
      · linarith;
    have h_card_le_sqrt : (insert 1 B).card ≤ 2 * Real.sqrt (M : ℝ) := by
      nlinarith only [ Real.sqrt_nonneg M, Real.sq_sqrt ( Nat.cast_nonneg M ), ( by norm_cast : ( insert 1 B |> Finset.card : ℝ ) ^ 2 ≤ 4 * M ) ];
    refine' lt_of_le_of_lt h_card_le_sqrt _;
    convert sqrt_lt_rpow_three_fourths M ( by linarith ) using 1

end Erdos44
