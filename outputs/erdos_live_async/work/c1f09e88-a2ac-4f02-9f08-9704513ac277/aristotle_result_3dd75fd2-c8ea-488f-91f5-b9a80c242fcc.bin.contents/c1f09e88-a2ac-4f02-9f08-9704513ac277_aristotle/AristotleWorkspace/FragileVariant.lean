/-
# Falsifying witness for the most fragile variant of Erdős Problem 123

The original conjecture (Erdős Problem 123) states that for any three pairwise coprime
integers a, b, c > 1, the set {a^i · b^j · c^k : i, j, k ∈ ℕ} is d-complete.

The **most fragile observed variant** is obtained by dropping the pairwise-coprimality
hypothesis. We exhibit a concrete counterexample showing this weakened variant is false:

  **Witness**: a = 2, b = 4, c = 8.

These satisfy 1 < a, 1 < b, 1 < c, but ¬PairwiseCoprime3 2 4 8.
The multiplicative semigroup {2^i · 4^j · 8^k} collapses to {2^n : n ∈ ℕ}.
Since divisibility on powers of 2 is a total order, the only antichains
(under divisibility) are singletons, so the set of achievable antichain sums
is exactly {2^n : n ∈ ℕ} — a set of density zero, hence not d-complete.

In particular, the number 3 is never an antichain sum from this set.
-/
import Mathlib
import AristotleWorkspace.Erdos123

noncomputable section

namespace Erdos123

open Filter Finset
open scoped BigOperators

/-! ## Step 1: The power-triple set for (2,4,8) is exactly the powers of 2 -/

/-- Every element of PowTripleSet 2 4 8 is a power of 2. -/
lemma powTripleSet_2_4_8_subset_pow2 :
    PowTripleSet 2 4 8 ⊆ {n | ∃ m : ℕ, n = 2 ^ m} := by
  intro n hn
  obtain ⟨i, j, k, hn_eq⟩ := hn
  use i + 2 * j + 3 * k
  rw [hn_eq]
  norm_num [pow_add, pow_mul]

/-- Every power of 2 belongs to PowTripleSet 2 4 8. -/
lemma pow2_subset_powTripleSet_2_4_8 :
    {n | ∃ m : ℕ, n = 2 ^ m} ⊆ PowTripleSet 2 4 8 := by
  exact fun n hn => by obtain ⟨m, rfl⟩ := hn; exact ⟨m, 0, 0, by ring⟩

/-- The power-triple set for (2,4,8) equals the set of powers of 2. -/
lemma powTripleSet_2_4_8_eq :
    PowTripleSet 2 4 8 = {n | ∃ m : ℕ, n = 2 ^ m} :=
  Set.Subset.antisymm powTripleSet_2_4_8_subset_pow2 pow2_subset_powTripleSet_2_4_8

/-! ## Step 2: Divisibility on powers of 2 is a total order -/

/-- Among powers of 2, divisibility is a total order: one always divides the other. -/
lemma pow2_divides_total (a b : ℕ) : 2 ^ a ∣ 2 ^ b ∨ 2 ^ b ∣ 2 ^ a := by
  cases le_total a b <;> simp +decide [*, pow_dvd_pow]

/-! ## Step 3: Antichain subsets of powers of 2 have at most one element -/

/-- Any division-antichain drawn from powers of 2 is a singleton or empty. -/
lemma antichain_pow2_card_le_one (s : Finset ℕ)
    (hs : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m})
    (hac : IsDivisionAntichain s) :
    s.card ≤ 1 := by
  by_contra h_contra
  obtain ⟨x, y, hx, hy, hxy⟩ : ∃ x y : ℕ, x ∈ s ∧ y ∈ s ∧ x ≠ y :=
    Finset.one_lt_card_iff.1 (lt_of_not_ge h_contra)
  obtain ⟨a, rfl⟩ := hs hx
  obtain ⟨b, rfl⟩ := hs hy
  exact hac hx hy hxy (pow2_divides_total a b |>.resolve_right <| by aesop)

/-! ## Step 4: An antichain sum from powers of 2 is itself a power of 2 -/

/-- An antichain sum from a subset of {2^n} must itself be a power of 2 (or 0). -/
lemma antichain_sum_is_pow2 (s : Finset ℕ)
    (hs : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m})
    (hac : IsDivisionAntichain s) :
    ∃ m : ℕ, s.sum id = 2 ^ m ∨ s.sum id = 0 := by
  by_cases h : s.Nonempty
  · have h_singleton : s.card = 1 :=
      le_antisymm (antichain_pow2_card_le_one s hs hac) (Finset.card_pos.mpr h)
    rw [Finset.card_eq_one] at h_singleton; aesop
  · aesop

/-! ## Step 5: 3 is not a power of 2 -/

/-- 3 is not a power of 2. -/
lemma three_ne_pow2 : ∀ m : ℕ, 3 ≠ 2 ^ m := by
  intro m hm
  linarith [Nat.pow_le_pow_right (show 1 ≤ 2 by norm_num)
    (show m ≥ 2 by contrapose! hm; interval_cases m <;> trivial)]

/-! ## Step 6: 3 cannot be represented as an antichain sum from PowTripleSet 2 4 8 -/

/-- The number 3 has no antichain sum representation in PowTripleSet 2 4 8. -/
lemma no_antichain_sum_3 :
    ¬ ∃ s : Finset ℕ,
      (↑s : Set ℕ) ⊆ PowTripleSet 2 4 8 ∧
      IsDivisionAntichain s ∧
      s.sum id = 3 := by
  by_contra h_contra
  obtain ⟨s, hs⟩ := h_contra
  have hs_subset : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m} :=
    hs.1.trans powTripleSet_2_4_8_eq.le
  have hs_antichain : IsDivisionAntichain s := hs.2.1
  have hs_sum : s.sum id = 3 := by grobner
  obtain ⟨m, hm⟩ := antichain_sum_is_pow2 s hs_subset hs_antichain
  have h_contradiction : 3 = 2 ^ m ∨ 3 = 0 := by grind +ring
  exact h_contradiction.elim (three_ne_pow2 m) (by norm_num)

/-! ## Step 7: The set PowTripleSet 2 4 8 is NOT d-complete -/

/-- PowTripleSet 2 4 8 is not d-complete — the non-coprime variant of Erdős 123 is false. -/
theorem not_d_complete_2_4_8 : ¬ IsDComplete (PowTripleSet 2 4 8) := by
  intro h
  obtain ⟨s, hs₁, hs₂, hs₃⟩ :
      ∃ s : Finset ℕ, (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m} ∧
        IsDivisionAntichain s ∧ s.sum id = 3 := by
    obtain ⟨N, hN⟩ := Filter.eventually_atTop.mp h
    obtain ⟨s, hs₁, hs₂, hs₃⟩ := hN (2 * N + 3) (by linarith)
    obtain ⟨m, hm⟩ := antichain_sum_is_pow2 s
      (fun x hx => by have := hs₁ hx; exact powTripleSet_2_4_8_eq.subset this) hs₂
    simp_all +decide
    have := congr_arg Even hm; norm_num [Nat.even_add, Nat.even_pow] at this; aesop
  obtain ⟨m, hm⟩ := antichain_sum_is_pow2 s hs₁ hs₂
  rcases hm with hm | hm <;>
    linarith [Nat.pow_le_pow_right (show 1 ≤ 2 by norm_num)
      (show m ≥ 2 by contrapose! hm; interval_cases m <;> linarith)]

/-! ## Step 8: (2, 4, 8) are NOT pairwise coprime -/

/-- The triple (2, 4, 8) is not pairwise coprime. -/
lemma not_pairwiseCoprime_2_4_8 : ¬ PairwiseCoprime3 2 4 8 := by
  unfold PairwiseCoprime3; norm_num

/-! ## Main result: the non-coprime variant of Erdős 123 is false -/

/-- **Falsifying witness for the most fragile variant.**
Dropping the pairwise-coprimality hypothesis from Erdős Problem 123 renders the
statement false. The triple (2, 4, 8) witnesses this. -/
theorem erdos_123_fragile_variant_false :
    ¬ (∀ a b c : ℕ, 1 < a → 1 < b → 1 < c → IsDComplete (PowTripleSet a b c)) := by
  intro h
  exact not_d_complete_2_4_8 (h 2 4 8 (by norm_num) (by norm_num) (by norm_num))

end Erdos123
