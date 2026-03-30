/-
Experiment ID: 233580d4-c454-41ec-a83d-04187d52e451
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

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
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
## Fragility witness: the (1+ε) strengthening is provably false

The conjecture `erdos_44_sidon_extension` asks for `(1 - ε) * √M ≤ |A ∪ B|`. We show that
replacing `(1 - ε)` with `(1 + ε)` yields a **false** statement. This is a tight upper-bound
barrier: the Erdős–Turán counting argument shows that every Sidon subset of `[1, M]` has
strictly fewer than `2√M` elements, which refutes the `ε = 1` case of the strengthening.

### Mathematical argument (Erdős–Turán upper bound, simplified)

If `A ⊆ {1, …, M}` is a Sidon set with `n = |A|`, the `n(n-1)/2` pairwise differences
`a - b` (for `a > b` in `A`) are distinct elements of `{1, …, M - 1}`, giving
`n(n-1)/2 ≤ M - 1`. Rearranging, `n < (1 + √(8M - 7)) / 2 < 2√M` for all `M ≥ 1`.

Hence no Sidon subset of `[1, M]` can reach cardinality `2√M = (1 + 1) · √M`, and the
(1 + ε) variant fails already at `ε = 1`.
-/

/-- Key counting lemma (Erdős–Turán): for a Sidon set `A ⊆ [1, M]`, we have
`|A| * (|A| - 1) ≤ 2 * (M - 1)`. This follows from the fact that the
`|A| * (|A| - 1) / 2` pairwise differences `a - b` (for `a > b` in `A`) are
distinct and lie in `{1, …, M - 1}`. -/
theorem sidon_card_bound (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    A.card * (A.card - 1) ≤ 2 * (M - 1) := by
  have h_diff_distinct : (Finset.image (fun (p : ℕ × ℕ) => p.1 - p.2)
      (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A))).card =
      A.card * (A.card - 1) / 2 := by
    have h_comb : (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A)).card =
        A.card * (A.card - 1) / 2 := by
      have h_pairs : (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A)).card =
          Finset.card (Finset.powersetCard 2 A) := by
        refine' Finset.card_bij (fun p _ => {p.1, p.2}) _ _ _ <;>
          simp_all +decide [Finset.mem_powersetCard]
        · exact fun a b ha hb hab =>
            ⟨Finset.insert_subset_iff.mpr
              ⟨ha, Finset.singleton_subset_iff.mpr hb⟩,
            by rw [Finset.card_insert_of_notMem, Finset.card_singleton]; aesop⟩
        · simp +contextual [Finset.Subset.antisymm_iff, Finset.subset_iff]
          intros; omega
        · intro b hb hb'
          rw [Finset.card_eq_two] at hb'
          obtain ⟨a, b, hab, rfl⟩ := hb'
          cases lt_trichotomy a b <;> aesop
      rw [h_pairs, Finset.card_powersetCard, Nat.choose_two_right]
    rw [← h_comb, Finset.card_image_of_injOn]
    intro p hp q hq h_eq
    have := @hS p.1 q.2 q.1 p.2
    simp_all +decide
    grind
  have h_diff_bound : (Finset.image (fun (p : ℕ × ℕ) => p.1 - p.2)
      (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A))).card ≤ M - 1 := by
    have h_sub : (Finset.image (fun (p : ℕ × ℕ) => p.1 - p.2)
        (Finset.filter (fun p => p.1 > p.2) (A ×ˢ A))) ⊆ Finset.Icc 1 (M - 1) := by
      grind +revert
    exact le_trans (Finset.card_le_card h_sub) (by simpa)
  linarith [Nat.div_mul_cancel
    (show 2 ∣ #A * (#A - 1) from even_iff_two_dvd.mp (Nat.even_mul_pred_self _))]

/-- For any Sidon set `A ⊆ [1, M]`, we have `|A| < 2 * √M`. This is a corollary of
`sidon_card_bound` via the algebraic fact that `n ≥ 2√M` implies `n*(n-1) ≥ 2*M`. -/
theorem sidon_card_lt_two_sqrt (A : Finset ℕ) (M : ℕ) (hM : 1 ≤ M)
    (hA : A ⊆ Finset.Icc 1 M) (hS : IsSidonFinset A) :
    (A.card : ℝ) < 2 * Real.sqrt (M : ℝ) := by
  set n := A.card with hn
  have h_bound : n * (n - 1) ≤ 2 * (M - 1) := sidon_card_bound A M hM hA hS
  rcases n with (_ | _ | n) <;> norm_num at *
  · linarith
  · nlinarith only [show (M : ℝ) ≥ 1 by norm_cast, Real.sqrt_nonneg M,
      Real.sq_sqrt (Nat.cast_nonneg M)]
  · rcases M with (_ | _ | M) <;> norm_num at *
    nlinarith only [Real.sqrt_nonneg (M + 1 + 1),
      Real.sq_sqrt (show (M : ℝ) + 1 + 1 ≥ 0 by positivity),
      (by norm_cast : (n + 1 + 1 : ℝ) * (n + 1) ≤ 2 * (M + 1))]

/-- **Fragility witness (falsifying the (1+ε) strengthening).**

The variant of Erdős Problem 44 obtained by replacing `(1 - ε)` with `(1 + ε)` is **false**.
Taking `ε = 1`, the strengthened statement would require a Sidon subset of `[1, M]` of
cardinality `≥ 2√M`, which is ruled out by `sidon_card_lt_two_sqrt`.

This is an upper-bound barrier showing the original `(1 - ε)` factor sits right at the
boundary of what is compatible with the Sidon cardinality ceiling; any upward perturbation
of the multiplicative constant past `1` renders the statement provably false.

The witness is `ε = 1` with `A = {1}` and `N = 1`. For any `M`, `|A ∪ B| < 2√M` by the
Erdős–Turán bound, contradicting the strengthened requirement `2√M ≤ |A ∪ B|`. -/
theorem erdos_44_strengthened_is_false :
    ¬ (∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 + ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  push_neg
  refine ⟨1, zero_lt_one, ?_⟩
  intro Mε
  use 1
  simp
  refine Or.inr ⟨?_, ?_⟩
  · intro a b c d ha hb hc hd habcd; aesop
  · intro M hM₁ hM₂ B hB hS
    have := @sidon_card_lt_two_sqrt (insert 1 B) M hM₁ ?_ hS <;>
      simp_all +decide [Finset.subset_iff]
    · linarith
    · exact fun x hx => by linarith [hB hx]

end Erdos44
