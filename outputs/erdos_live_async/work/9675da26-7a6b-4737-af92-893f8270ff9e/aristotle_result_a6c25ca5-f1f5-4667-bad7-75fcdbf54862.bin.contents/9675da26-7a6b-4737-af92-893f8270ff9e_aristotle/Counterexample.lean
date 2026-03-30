/-
Counterexample to the "most fragile variant" of Erdős Problem 123.

The full conjecture asserts d-completeness for PowTripleSet a b c when a, b, c > 1
are pairwise coprime. The most fragile variant drops pairwise coprimality.

Falsifying witness: a = b = c = 2.
  PowTripleSet 2 2 2 = {2^n | n ∈ ℕ},
and any division-antichain in powers of 2 is a singleton or empty (since 2^a ∣ 2^b
for a ≤ b). So achievable antichain sums are exactly {0} ∪ {2^n : n ∈ ℕ},
which misses every odd number ≥ 3.
-/
import Mathlib

open Filter Finset
open scoped BigOperators

noncomputable section

namespace Erdos123Counterexample

def PowTripleSet (a b c : ℕ) : Set ℕ :=
  {n | ∃ i j k : ℕ, n = a ^ i * b ^ j * c ^ k}

def IsDivisionAntichain (s : Finset ℕ) : Prop :=
  ∀ ⦃x y : ℕ⦄, x ∈ s → y ∈ s → x ≠ y → ¬ x ∣ y

def IsDComplete (A : Set ℕ) : Prop :=
  ∀ᶠ n : ℕ in atTop, ∃ s : Finset ℕ,
    (↑s : Set ℕ) ⊆ A ∧ IsDivisionAntichain s ∧ s.sum id = n

/-
PROBLEM
Every element of PowTripleSet 2 2 2 is a power of 2.

PROVIDED SOLUTION
Extensionality: n ∈ PowTripleSet 2 2 2 iff ∃ i j k, n = 2^i * 2^j * 2^k iff ∃ i j k, n = 2^(i+j+k) iff ∃ m, n = 2^m. Forward: given i,j,k, take m = i+j+k, use pow_add. Backward: given m, take i=m, j=0, k=0.
-/
lemma powTripleSet_222_eq :
    PowTripleSet 2 2 2 = {n | ∃ m : ℕ, n = 2 ^ m} := by
  -- To prove equality of sets, we show each set is a subset of the other.
  apply Set.ext
  intro n
  simp [PowTripleSet];
  exact ⟨ fun ⟨ i, j, k, h ⟩ => ⟨ i + j + k, by rw [ h, ← pow_add, ← pow_add ] ⟩, fun ⟨ m, h ⟩ => ⟨ 0, 0, m, by simpa using h ⟩ ⟩

/-
PROBLEM
Among powers of 2, any two distinct elements satisfy a divisibility relation,
    so any division-antichain has at most one element.

PROVIDED SOLUTION
By contradiction: if s.card ≥ 2, pick two distinct elements x, y ∈ s. By hs, x = 2^a and y = 2^b. Since x ≠ y, a ≠ b. WLOG a < b (use Nat.lt_or_gt_of_ne). Then x = 2^a divides y = 2^b by Nat.pow_dvd_pow. But ha says ¬(x ∣ y), contradiction.
-/
lemma antichain_pow2_card_le_one (s : Finset ℕ)
    (hs : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m})
    (ha : IsDivisionAntichain s) : s.card ≤ 1 := by
  -- Assume there are two distinct elements $x, y \in s$.
  by_contra h_contra
  obtain ⟨x, y, hx, hy, hxy⟩ : ∃ x y : ℕ, x ∈ s ∧ y ∈ s ∧ x ≠ y := by
    simpa using Finset.one_lt_card.mp ( not_le.mp h_contra );
  obtain ⟨ m₁, rfl ⟩ := hs hx; obtain ⟨ m₂, rfl ⟩ := hs hy; cases lt_trichotomy m₁ m₂ <;> simp_all +decide [ Nat.pow_dvd_pow_iff ] ;
  · exact ha hx hy ( by aesop ) ( pow_dvd_pow _ ( le_of_lt ‹_› ) );
  · exact ha hy hx ( by aesop ) ( pow_dvd_pow _ ( le_of_lt ‹_› ) )

/-
PROBLEM
A finset of naturals with at most one element sums to either 0 or its unique element.

PROVIDED SOLUTION
If s.card = 0, s is empty, sum = 0, Left case. If s.card = 1, then s = {x} for some x, and sum = x. Right case with that x.
-/
lemma sum_of_card_le_one (s : Finset ℕ) (h : s.card ≤ 1) :
    s.sum id = 0 ∨ ∃ x ∈ s, s.sum id = x ∧ s = {x} := by
  cases s using Finset.induction <;> aesop

/-
PROBLEM
An odd number ≥ 3 is not 0 and not a power of 2.

PROVIDED SOLUTION
n is odd and ≥ 3, so n ≠ 0. For the second part: if n = 2^m, then for m = 0 we get n = 1 < 3, contradiction. For m ≥ 1, 2^m is even, but n is odd, contradiction (use Nat.even_pow or Even.pow).
-/
lemma odd_not_pow2 {n : ℕ} (hn : Odd n) (hn3 : 3 ≤ n) :
    n ≠ 0 ∧ ∀ m : ℕ, n ≠ 2 ^ m := by
  grind

/-
PROBLEM
PowTripleSet 2 2 2 is not d-complete: odd numbers ≥ 3 are never antichain sums.

PROVIDED SOLUTION
Unfold IsDComplete. We get: ∀ᶠ n in atTop, ∃ s, s ⊆ PowTripleSet 2 2 2 ∧ antichain s ∧ s.sum id = n. This means ∃ N, ∀ n ≥ N, ∃ s with those properties. Pick n = 2 * max N 2 + 1, which is ≥ N, odd, and ≥ 5 (so ≥ 3). For such n, we'd get an antichain s ⊆ PowTripleSet 2 2 2. By powTripleSet_222_eq, s ⊆ {2^m}. By antichain_pow2_card_le_one, s.card ≤ 1. By sum_of_card_le_one, sum is 0 or a single element 2^m. But n is odd and ≥ 3, so by odd_not_pow2, n ≠ 0 and n ≠ 2^m for any m. Contradiction.
-/
theorem powTripleSet_222_not_dComplete :
    ¬ IsDComplete (PowTripleSet 2 2 2) := by
  -- Assume for contradiction that PowTripleSet 2 2 2 is d-complete.
  by_contra h_d_complete

  -- By definition of d-complete, there exists some N such that for all n ≥ N, n can be expressed as a sum of a division-antichain in PowTripleSet 2 2 2.
  obtain ⟨N, hN⟩ : ∃ N, ∀ n ≥ N, ∃ s : Finset ℕ, (s : Set ℕ) ⊆ PowTripleSet 2 2 2 ∧ IsDivisionAntichain s ∧ s.sum id = n := by
    exact Filter.eventually_atTop.mp h_d_complete;
  -- Consider the odd number $n = 2N + 3$. Since $n \geq N$, by the definition of $d$-completeness, there must exist a division-antichain $s$ in $PowTripleSet 2 2 2$ such that $s.sum id = n$.
  obtain ⟨s, hs⟩ : ∃ s : Finset ℕ, (s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m} ∧ IsDivisionAntichain s ∧ s.sum id = 2 * N + 3 := by
    exact hN _ ( by linarith ) |> fun ⟨ s, hs₁, hs₂, hs₃ ⟩ => ⟨ s, hs₁.trans ( powTripleSet_222_eq ▸ Set.Subset.refl _ ), hs₂, hs₃ ⟩;
  -- By the lemma sum_of_card_le_one, the sum of elements in s is either 0 or a single element 2^m.
  obtain ⟨m, hm⟩ : ∃ m : ℕ, s.sum id = 2 ^ m := by
    have := antichain_pow2_card_le_one s hs.1 hs.2.1; ( have := sum_of_card_le_one s this; aesop; ) ;
  generalize_proofs at *; simp_all +decide [ IsDComplete ] ; (
  have := congr_arg Even hm; norm_num [ Nat.even_add, Nat.even_pow ] at this; rcases m with ( _ | _ | m ) <;> simp_all +decide [ Nat.pow_succ' ] ;)

/-- The variant of Erdős 123 without the coprimality hypothesis is **false**. -/
theorem erdos_123_fragile_variant_false :
    ¬ (∀ a b c : ℕ, 1 < a → 1 < b → 1 < c →
      IsDComplete (PowTripleSet a b c)) := by
  intro h
  exact powTripleSet_222_not_dComplete (h 2 2 2 (by norm_num) (by norm_num) (by norm_num))

end Erdos123Counterexample