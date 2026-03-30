/-
Counterexample / independence-style witnesses for the most fragile observed
variant of Erdős Problem 44 (Sidon extension with near-optimal density).

The fragility of `erdos_44_sidon_extension` concentrates at two points:
  (F1) The density coefficient (1 - ε) × √M must be achievable for EVERY
       starting Sidon set A, including adversarial ones that block many
       nearby elements.
  (F2) The quantifier order  ∀ε>0, ∃Mε, ∀N, ∀A, ∃M …  forces Mε to be
       chosen *before* N and A are revealed; so the same threshold must
       work for arbitrarily large, adversarial inputs.

Below we provide:
  • The Erdős–Turán counting-argument upper bound |A|² ≤ 4N for Sidon
    A ⊆ [1,N], proving the density constraint is tight.
  • A concrete blocked-extension witness: {1,2,5} is Sidon, but
    {1,2,5,6} is NOT, because 1+6 = 2+5 = 7 (obstruction to greedy
    extension at the very next element).
  • Falsification of the "coefficient ≥ 2" strengthened variant: replacing
    the factor (1-ε) with 2 yields a provably false statement, since
    the Erdős–Turán bound caps Sidon density at 2√N.
  • The tight corollary |A| ≤ 2√N, showing the (1-ε)√M target is the
    tightest possible up to the leading constant.
-/

import Mathlib

noncomputable section

namespace Erdos44

open Finset

/-- Sidon condition (same as Main.lean). -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ## Section 1 — Concrete Sidon witnesses -/

/-- The set {1, 2, 5} is a Sidon set. -/
theorem isSidon_one_two_five : IsSidonFinset {1, 2, 5} := by
  intros a b c d ha hb hc hd habcd; simp_all +arith +decide; omega

/-- The set {1, 2, 5, 6} is NOT a Sidon set, because 1 + 6 = 2 + 5 = 7
    but {1, 6} ≠ {2, 5}. This is the simplest blocked-extension witness:
    {1, 2, 5} is Sidon but cannot be extended to include 6. -/
theorem not_isSidon_one_two_five_six : ¬ IsSidonFinset {1, 2, 5, 6} := by
  simp [IsSidonFinset]

/-! ## Section 2 — Sidon counting upper bound (Erdős–Turán) -/

/-- **Erdős–Turán counting bound.** For a Sidon set A ⊆ [1, N],
    the sum map (a, b) ↦ a + b on A × A has at most 2-to-1 fibers
    (by the Sidon property) and image contained in [2, 2N].
    Counting gives |A|² ≤ 2 · (2N − 1) ≤ 4N. -/
theorem sidon_card_sq_le (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    A.card * A.card ≤ 4 * N := by
  have h_distinct_sums :
      (Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (A ×ˢ A)).card ≤ 2 * N - 1 := by
    exact le_trans (Finset.card_le_card (Finset.image_subset_iff.2 fun p hp =>
      show p.1 + p.2 ∈ Finset.Icc 2 (2 * N) from Finset.mem_Icc.2
        ⟨by linarith [Finset.mem_Icc.1 (hA <| Finset.mem_product.1 hp |>.1),
                       Finset.mem_Icc.1 (hA <| Finset.mem_product.1 hp |>.2)],
         by linarith [Finset.mem_Icc.1 (hA <| Finset.mem_product.1 hp |>.1),
                       Finset.mem_Icc.1 (hA <| Finset.mem_product.1 hp |>.2)]⟩))
      (by norm_num; omega)
  have h_two_to_one :
      ∀ s ∈ Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (A ×ˢ A),
        (Finset.filter (fun p => p.1 + p.2 = s) (A ×ˢ A)).card ≤ 2 := by
    intro s hs
    have h_swap : ∀ p q : ℕ × ℕ, p ∈ A ×ˢ A → q ∈ A ×ˢ A →
        p.1 + p.2 = s → q.1 + q.2 = s → p = q ∨ p = (q.2, q.1) := by
      intros p q hp hq hp_eq hq_eq; specialize hS; aesop
    obtain ⟨p, hp⟩ := Finset.mem_image.mp hs
    exact le_trans (Finset.card_le_card <|
      show {p ∈ A ×ˢ A | p.1 + p.2 = s} ⊆ {p, (p.2, p.1)} from
        fun q hq => by specialize h_swap q p; aesop)
      (Finset.card_insert_le _ _)
  have h_total_pairs :
      (A ×ˢ A).card ≤ 2 * (Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (A ×ˢ A)).card :=
    card_le_mul_card_image (A ×ˢ A) 2 h_two_to_one
  norm_num at *; omega

/-! ## Section 3 — Falsification of the "coefficient ≥ 2" strengthened variant -/

/-- **The coefficient-2 variant is provably false.** If we replace the factor
    (1 − ε) in `erdos_44_sidon_extension` with 2 (i.e. demand
    2√M < |A ∪ B|), the resulting statement is false: the Erdős–Turán
    bound |A ∪ B|² ≤ 4M forces |A ∪ B| ≤ 2√M for any Sidon set in [1, M].

    Witness: N = 1, A = {1}. For any M ≥ 1 and any Sidon extension
    {1} ∪ B ⊆ [1, M], we have |{1} ∪ B| ≤ 2√M, contradicting 2√M < |{1} ∪ B|. -/
theorem strengthened_variant_coeff_two_false :
    ¬ (∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ N ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            2 * Real.sqrt (M : ℝ) < ((A ∪ B).card : ℝ)) := by
  push_neg
  use 1, by norm_num, {1}; norm_num
  refine ⟨by unfold IsSidonFinset; aesop, ?_⟩
  intro M hM B hB hS
  have h_card : (insert 1 B).card * (insert 1 B).card ≤ 4 * M :=
    sidon_card_sq_le (insert 1 B) M hM (by grind +splitImp) hS
  nlinarith only [Real.sqrt_nonneg M, Real.sq_sqrt (Nat.cast_nonneg M),
    (by norm_cast : ((insert 1 B).card : ℝ) * (insert 1 B).card ≤ 4 * M)]

/-! ## Section 4 — The (1-ε) bound is tight: Sidon sets cannot exceed 2√N -/

/-- **Tight density bound.** No Sidon set in [1, N] can have more than
    2√N elements. This shows that the (1 − ε)√M target in the original
    theorem is the tightest possible up to the leading constant:
    improving (1 − ε) to any constant c > 2 is provably impossible. -/
theorem sidon_card_le_two_sqrt (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    (A.card : ℝ) ≤ 2 * Real.sqrt N := by
  nlinarith [Real.sqrt_nonneg N, Real.sq_sqrt (Nat.cast_nonneg N),
    show (A.card : ℝ) * A.card ≤ 4 * N by exact_mod_cast sidon_card_sq_le A N hN hA hS]

/-! ## Section 5 — Basic Sidon set constructions -/

/-- The empty set is trivially Sidon. -/
theorem empty_sidon : IsSidonFinset ∅ := by
  intros a b c d ha; simp at ha

/-- A singleton set is Sidon. -/
theorem singleton_sidon (n : ℕ) (_hn : 1 ≤ n := by omega) : IsSidonFinset {n} := by
  intro a b c d ha hb hc hd _; aesop

/-- A two-element set {a, b} with a ≠ b is Sidon. -/
theorem pair_sidon {a b : ℕ} (_hab : a ≠ b) : IsSidonFinset {a, b} := by
  intro x y z t hx hy hz ht h; simp_all +decide; omega

end Erdos44
