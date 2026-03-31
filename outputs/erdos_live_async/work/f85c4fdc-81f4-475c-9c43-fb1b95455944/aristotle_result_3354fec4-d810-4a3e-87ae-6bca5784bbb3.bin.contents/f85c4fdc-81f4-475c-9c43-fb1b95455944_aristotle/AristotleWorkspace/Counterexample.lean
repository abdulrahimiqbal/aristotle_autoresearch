/-
  Counterexample for the negated weakening of Erdős Problem 123.

  The negated weakening drops the pairwise coprimality hypothesis and asks whether
  d-completeness still holds. We show it does NOT: for (a, b, c) = (2, 4, 8),
  the PowTripleSet is exactly {2^n : n ∈ ℕ} (the powers of 2). Any divisibility
  antichain from this set has at most one element, so only powers of 2 can be
  represented as antichain sums — in particular, 3 (or any non-power-of-2) cannot.

  Discovery question answer:
  The sharpest boundary witness is (2, 4, 8): interval-style coverage succeeds
  (every positive integer is a sum of distinct powers of 2 by binary representation)
  but the antichain upgrade fails catastrophically because every pair in {2^n}
  has a divisibility relation. More generally, whenever a | b or a | c or b | c,
  the antichain constraint becomes strictly more restrictive, and when all three
  generators share a common prime factor (e.g., all are powers of 2), the antichain
  constraint collapses to singletons.
-/
import Mathlib

noncomputable section

namespace Erdos123.Counterexample

open Filter Finset
open scoped BigOperators Pointwise

-- Re-state relevant definitions locally for self-containedness
def PowTripleSet (a b c : ℕ) : Set ℕ :=
  {n | ∃ i j k : ℕ, n = a ^ i * b ^ j * c ^ k}

def IsDivisionAntichain (s : Finset ℕ) : Prop :=
  ∀ ⦃x y : ℕ⦄, x ∈ s → y ∈ s → x ≠ y → ¬ x ∣ y

def IsDComplete (A : Set ℕ) : Prop :=
  ∀ᶠ n : ℕ in atTop, ∃ s : Finset ℕ,
    (↑s : Set ℕ) ⊆ A ∧ IsDivisionAntichain s ∧ s.sum id = n

/-! ## Key lemma: PowTripleSet 2 4 8 = {2^n : n ∈ ℕ} -/

/-
PROBLEM
Every element of PowTripleSet 2 4 8 is a power of 2.

PROVIDED SOLUTION
Show set equality by extensionality. For the forward direction: if n = 2^i * 4^j * 8^k = 2^i * 2^(2j) * 2^(3k) = 2^(i+2j+3k), take m = i+2j+3k. For the backward direction: if n = 2^m, take i=m, j=0, k=0 and note 4^0 = 1 and 8^0 = 1.
-/
lemma powTripleSet_248_eq_pow2 :
    PowTripleSet 2 4 8 = {n | ∃ m : ℕ, n = 2 ^ m} := by
  ext n;
  constructor;
  · rintro ⟨ i, j, k, rfl ⟩;
    exact ⟨ i + 2 * j + 3 * k, by norm_num [ pow_add, pow_mul ] ⟩;
  · rintro ⟨ m, rfl ⟩ ; exact ⟨ m, 0, 0, by ring ⟩ ;

/-! ## Key lemma: antichains in powers of 2 have at most one element -/

/-
PROBLEM
In {2^n}, any two distinct elements have a divisibility relation,
    so a divisibility antichain has cardinality ≤ 1.

PROVIDED SOLUTION
Prove by contradiction. Suppose s.card ≥ 2. Then there exist distinct x, y ∈ s with x ≠ y. By hs, x = 2^a and y = 2^b for some a, b. Since x ≠ y, a ≠ b. WLOG a < b (use Nat.lt_or_gt_of_ne). Then 2^a ∣ 2^b (by Nat.pow_dvd_pow), contradicting hac (IsDivisionAntichain). Use Finset.one_lt_card to get the two distinct elements.
-/
lemma antichain_pow2_card_le_one (s : Finset ℕ)
    (hs : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m})
    (hac : IsDivisionAntichain s) :
    s.card ≤ 1 := by
  contrapose! hac;
  obtain ⟨ x, hx, y, hy, hxy ⟩ := Finset.one_lt_card.mp hac;
  obtain ⟨ m, rfl ⟩ := hs hx; obtain ⟨ n, rfl ⟩ := hs hy; cases lt_or_gt_of_ne hxy <;> simp_all +decide [ IsDivisionAntichain ] ;
  · exact ⟨ _, hx, _, hy, by aesop, pow_dvd_pow _ <| le_of_lt <| Nat.lt_of_not_ge fun h => by linarith [ pow_le_pow_right₀ ( by decide : 1 ≤ 2 ) h ] ⟩;
  · exact ⟨ _, hy, _, hx, by aesop, pow_dvd_pow _ <| le_of_lt <| Nat.lt_of_not_ge fun h => by linarith [ pow_le_pow_right₀ ( by decide : 1 ≤ 2 ) h ] ⟩

/-! ## Consequence: antichain sum from PowTripleSet 2 4 8 is at most one power of 2 -/

/-
PROBLEM
An antichain-sum from {2^n} of cardinality ≤ 1 is either 0 or a single power of 2.

PROVIDED SOLUTION
By antichain_pow2_card_le_one, s.card ≤ 1. Case split on s.card = 0 (then s = ∅, sum = 0, Left) or s.card = 1 (then s = {x} for some x, and by hs x is 2^m, so sum = 2^m, Right). Use Finset.card_le_one_iff or Finset.card_eq_zero / Finset.card_eq_one.
-/
lemma antichain_sum_pow2 (s : Finset ℕ)
    (hs : (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m})
    (hac : IsDivisionAntichain s) :
    s.sum id = 0 ∨ ∃ m : ℕ, s.sum id = 2 ^ m := by
  have := antichain_pow2_card_le_one s hs hac; interval_cases _ : #s <;> simp_all +decide ;
  rw [ Finset.card_eq_one ] at * ; aesop

/-! ## 3 is not a power of 2 -/

/-
PROVIDED SOLUTION
By induction/cases on m. For m=0: 2^0=1≠3. For m=1: 2^1=2≠3. For m≥2: 2^m ≥ 4 > 3. Use omega or interval_cases for small cases and monotonicity for larger ones.
-/
lemma three_not_pow2 : ∀ m : ℕ, 3 ≠ 2 ^ m := by
  intro m hm; linarith [ Nat.pow_le_pow_right ( show 1 ≤ 2 by norm_num ) ( show m ≥ 2 by contrapose! hm; interval_cases m <;> trivial ) ] ;

/-! ## The number 3 is not representable as an antichain sum -/

/-
PROVIDED SOLUTION
Suppose ⟨s, hsub, hac, hsum⟩. Rewrite hsub using powTripleSet_248_eq_pow2 to get s ⊆ {2^m}. By antichain_sum_pow2, s.sum id = 0 ∨ ∃ m, s.sum id = 2^m. Since hsum says s.sum id = 3, the first case gives 3 = 0 (contradiction), the second gives 3 = 2^m which contradicts three_not_pow2.
-/
lemma three_not_antichain_representable :
    ¬ ∃ s : Finset ℕ,
      (↑s : Set ℕ) ⊆ PowTripleSet 2 4 8 ∧
      IsDivisionAntichain s ∧ s.sum id = 3 := by
  grind +suggestions

/-! ## Main counterexample: PowTripleSet 2 4 8 is NOT d-complete -/

/-
PROBLEM
The negated weakening: dropping pairwise coprimality makes d-completeness fail.
    Specifically, (2, 4, 8) are all > 1 but NOT pairwise coprime, and their
    PowTripleSet is not d-complete.

PROVIDED SOLUTION
Unfold IsDComplete. We need to show the filter condition fails - i.e., not eventually true. Show that for all N, there exists n ≥ N such that n has no antichain representation. Use n = max N 3 (or just 3 if N ≤ 3, otherwise we need n ≥ N that's not a power of 2). Actually, simpler: show 3 is never representable using three_not_antichain_representable, then show the eventually condition implies it holds for n=3 (since 3 is eventually reached). More precisely, the filter atTop says ∃ N, ∀ n ≥ N, ..., so for n=3 (or any fixed non-power-of-2), it must hold for n=3, but three_not_antichain_representable says it doesn't. We can use Filter.Eventually.exists_forall_of_atTop or just unfold the filter and specialize to n = 3 once N ≤ 3.
-/
theorem negated_weakening_counterexample :
    ¬ IsDComplete (PowTripleSet 2 4 8) := by
  -- Rewrite IsDComplete definition. We need to show the filter condition fails - i.e., not eventually true.
  unfold IsDComplete;
  simp +zetaDelta at *;
  -- Let's choose any $x$ and derive a contradiction.
  intro x
  use 2 * x + 3;
  refine ⟨ by linarith, fun s hs₁ hs₂ hs₃ => ?_ ⟩;
  -- By antichain_sum_pow2, s.sum id = 0 ∨ ∃ m, s.sum id = 2 ^ m.
  have h_sum : s.sum id = 0 ∨ ∃ m, s.sum id = 2 ^ m := by
    grind +suggestions;
  obtain h | ⟨ m, hm ⟩ := h_sum <;> simp_all +arith +decide;
  have := congr_arg Even hm ; norm_num [ Nat.even_add, Nat.even_pow ] at this ; aesop

/-! ## Demonstrating interval coverage DOES hold (in contrast) -/

/-
PROBLEM
(For context) Every positive integer is a sum of distinct powers of 2
    by binary representation — this is the "interval coverage" that CANNOT
    be upgraded to antichain coverage. We state this but don't prove it
    formally as the proof requires bit-level induction.

PROVIDED SOLUTION
Use strong induction on n. For n > 0, consider n's binary representation. Take s = Finset.image (fun i => 2^i) (Finset.filter (fun i => n.testBit i) (Finset.range (n.log2 + 1))). This gives all powers of 2 appearing in n's binary expansion. The subset condition is trivial. The third condition (trivially true) is automatic. The sum equals n by Nat.sum_pow2_testBit or similar.

Actually a simpler approach: use Nat.bits or just prove by strong induction. If n is odd, write n = 1 + (n-1) where n-1 is even and positive if n ≥ 3, or handle n=1 directly. If n is even, n = 2*m, apply induction to m and scale the set.

Actually even simpler: the third condition is just `true` so it's trivially satisfied. We just need to find a finset of distinct powers of 2 summing to n. This is just binary representation. Use strong induction: for n=1, use {1}={2^0}. For n>1, n has a largest power of 2 ≤ n, say 2^k. Then apply induction to n - 2^k and add 2^k to the set.
-/
theorem interval_coverage_pow2 :
    ∀ n : ℕ, 0 < n → ∃ s : Finset ℕ,
      (↑s : Set ℕ) ⊆ {n | ∃ m : ℕ, n = 2 ^ m} ∧
      (∀ ⦃x y : ℕ⦄, x ∈ s → y ∈ s → x ≠ y → true) ∧
      s.sum id = n := by
  intro n hn; induction' n using Nat.strongRecOn with n ih; rcases Nat.even_or_odd' n with ⟨ k, rfl | rfl ⟩ <;> norm_num at *;
  · obtain ⟨ s, hs₁, hs₂ ⟩ := ih k ( by linarith ) hn; use s.image fun x => 2*x; simp_all +decide [ Finset.mul_sum _ _ _, Set.subset_def ] ;
    exact ⟨ fun x hx => by obtain ⟨ m, rfl ⟩ := hs₁ x hx; exact ⟨ m + 1, by ring ⟩, by rw [ ← hs₂, Finset.mul_sum _ _ _ ] ⟩;
  · rcases k with ( _ | k ) <;> simp_all +arith +decide;
    · exact ⟨ { 1 }, by norm_num; exact ⟨ 0, rfl ⟩ ⟩;
    · obtain ⟨ s, hs ⟩ := ih ( k + 1 ) ( by linarith ) ( by linarith );
      refine' ⟨ s.image ( fun x => 2 * x ) ∪ { 1 }, _, _ ⟩ <;> simp_all +decide [ Set.subset_def ];
      · exact ⟨ ⟨ 0, rfl ⟩, fun x hx => by obtain ⟨ m, rfl ⟩ := hs.1 x hx; exact ⟨ m + 1, by ring ⟩ ⟩;
      · rw [ ← Finset.mul_sum _ _ _, hs.2 ] ; ring

end Erdos123.Counterexample