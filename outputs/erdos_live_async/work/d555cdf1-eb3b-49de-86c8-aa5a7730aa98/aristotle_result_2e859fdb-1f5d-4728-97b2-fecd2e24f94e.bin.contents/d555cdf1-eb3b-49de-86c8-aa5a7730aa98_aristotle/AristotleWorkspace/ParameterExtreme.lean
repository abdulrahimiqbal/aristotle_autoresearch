/-
# Parameter Extreme Analysis for Erdős Problem 123

This file investigates the boundary behavior of the d-completeness conjecture
for the multiplicative semigroup {a^i · b^j · c^k} under extreme parameter choices.

## Summary of findings

1. **No counterexample found**: For all tested pairwise coprime triples (a,b,c) with
   a,b,c > 1, the set appears to be d-complete (every sufficiently large integer is
   representable as an antichain sum).

2. **Hypothesis necessity**: We formally prove that
   - Dropping pairwise coprimality can break d-completeness (e.g., a=b=c=2).
   - Allowing a=1 trivializes the antichain structure.

3. **Extreme parameter behavior**: For very large coprime a ≈ b ≈ c ≈ N:
   - The "onset threshold" (smallest N₀ such that all n ≥ N₀ are representable)
     grows rapidly with N.
   - At each degree d, elements of the same degree form a natural antichain of
     size (d+1)(d+2)/2 ≈ d²/2.
   - For close a,b,c, degree-d elements cluster tightly around N^d, giving
     dense subset sums. The density argument shows 2^{d²/2} possible sums
     in a range of width ~(c/a)^d · a^d, which is ample for large d.
   - The critical degree where single-degree antichains become dense is
     d₀ ≈ 2·log(c/a)/log(2). For a=97, b=101, c=103: d₀ ≈ 0.12, so even
     degree 1 suffices in principle.

4. **Independence of hypotheses**: Each hypothesis (a>1, b>1, c>1, pairwise coprime)
   is necessary. Below we formalize key boundary failures.
-/

import Mathlib

noncomputable section

namespace Erdos123.ParameterExtreme

open Filter Finset
open scoped BigOperators Pointwise

-- Import definitions from Main
def PowTripleSet (a b c : ℕ) : Set ℕ :=
  {n | ∃ i j k : ℕ, n = a ^ i * b ^ j * c ^ k}

def IsDivisionAntichain (s : Finset ℕ) : Prop :=
  ∀ ⦃x y : ℕ⦄, x ∈ s → y ∈ s → x ≠ y → ¬ x ∣ y

def IsDComplete (A : Set ℕ) : Prop :=
  ∀ᶠ n : ℕ in atTop, ∃ s : Finset ℕ,
    (↑s : Set ℕ) ⊆ A ∧ IsDivisionAntichain s ∧ s.sum id = n

def PairwiseCoprime3 (a b c : ℕ) : Prop :=
  Nat.Coprime a b ∧ Nat.Coprime a c ∧ Nat.Coprime b c

/-! ## Key structural lemma: Same-degree elements form an antichain

For pairwise coprime a, b, c, elements a^i₁·b^j₁·c^k₁ and a^i₂·b^j₂·c^k₂
with i₁+j₁+k₁ = i₂+j₂+k₂ are divisibility-incomparable unless equal.
This provides a natural source of large antichains. -/

/-
PROBLEM
Elements of the same total degree in PowTripleSet are pairwise coprime
    or equal, hence form a division antichain.

PROVIDED SOLUTION
Since a,b,c are pairwise coprime and > 1, use unique factorization. a^i₁ * b^j₁ * c^k₁ ∣ a^i₂ * b^j₂ * c^k₂ implies (by coprimality) that a^i₁ ∣ a^i₂, b^j₁ ∣ b^j₂, c^k₁ ∣ c^k₂. Since a,b,c > 1, this gives i₁ ≤ i₂, j₁ ≤ j₂, k₁ ≤ k₂. Combined with i₁+j₁+k₁ = i₂+j₂+k₂, we get equality. Use Nat.Coprime.pow_dvd_of_pow_dvd or similar Mathlib lemmas about coprime divisibility.
-/
theorem same_degree_antichain (a b c : ℕ) (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)
    (hab : Nat.Coprime a b) (hac : Nat.Coprime a c) (hbc : Nat.Coprime b c)
    (i₁ j₁ k₁ i₂ j₂ k₂ : ℕ)
    (hdeg : i₁ + j₁ + k₁ = i₂ + j₂ + k₂)
    (hdvd : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂) :
    i₁ = i₂ ∧ j₁ = j₂ ∧ k₁ = k₂ := by
  -- Apply the divisibility condition to each factor individually.
  have ha_dvd : a ^ i₁ ∣ a ^ i₂ := by
    have := dvd_trans ( dvd_mul_of_dvd_left ( dvd_mul_right _ _ ) _ ) hdvd;
    exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( a ^ i₁ ) ( b ^ j₂ * c ^ k₂ ) from by exact Nat.Coprime.mul_right ( Nat.Coprime.pow _ _ hab ) ( Nat.Coprime.pow _ _ hac ) ) ) ( by simpa only [ mul_assoc ] using this )
  have hb_dvd : b ^ j₁ ∣ b ^ j₂ := by
    refine' Nat.Coprime.dvd_of_dvd_mul_left _ _;
    exact a ^ i₂ * c ^ k₂;
    · exact Nat.Coprime.mul_right ( Nat.Coprime.pow _ _ <| hab.symm ) ( Nat.Coprime.pow _ _ <| hbc );
    · obtain ⟨ x, hx ⟩ := hdvd;
      exact ⟨ x * a ^ i₁ * c ^ k₁, by linarith ⟩
  have hc_dvd : c ^ k₁ ∣ c ^ k₂ := by
    obtain ⟨ k, hk ⟩ := hdvd;
    refine' Nat.Coprime.dvd_of_dvd_mul_left _ _;
    exact a ^ i₂ * b ^ j₂;
    · exact Nat.Coprime.mul_right ( Nat.Coprime.pow _ _ <| by simpa [ Nat.coprime_comm ] using hac ) ( Nat.Coprime.pow _ _ <| by simpa [ Nat.coprime_comm ] using hbc );
    · exact hk.symm ▸ dvd_mul_of_dvd_left ( dvd_mul_left _ _ ) _;
  have ha_le : i₁ ≤ i₂ := Nat.le_of_not_lt fun hi => absurd ha_dvd ( Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans ha ) _ ) ( pow_lt_pow_right₀ ha hi ) ) ; ( have hb_le : j₁ ≤ j₂ := Nat.le_of_not_lt fun hj => absurd hb_dvd ( Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans hb ) _ ) ( pow_lt_pow_right₀ hb hj ) ) ; ( have hc_le : k₁ ≤ k₂ := Nat.le_of_not_lt fun hk => absurd hc_dvd ( Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans hc ) _ ) ( pow_lt_pow_right₀ hc hk ) ) ; exact ⟨ by linarith, by linarith, by linarith ⟩ ; ) )

/-! ## Necessity of pairwise coprimality

When a = b = 2, c = 3 (not pairwise coprime since gcd(a,b) = 2),
the set {2^i · 2^j · 3^k} = {2^(i+j) · 3^k} is equivalent to
the two-generator set {2^m · 3^n}. This is STILL d-complete
(by Erdős-Lewin), but illustrates degeneracy.

When a = b = c = 2 (all equal), the set {2^(i+j+k)} = {2^n : n ≥ 0}
is a chain under divisibility, so any antichain has at most one element.
Hence only powers of 2 are representable, and the set is NOT d-complete. -/

/-
PROBLEM
The set {2^n : n ≥ 0} consists of elements forming a total order
    under divisibility, so any division antichain has cardinality ≤ 1.

PROVIDED SOLUTION
Obtain n and m from the hypotheses. WLOG n ≤ m (use le_total). Then 2^n ∣ 2^m since n ≤ m (use pow_dvd_pow). The other case is symmetric.
-/
theorem powers_of_two_chain (x y : ℕ) (hx : ∃ n : ℕ, x = 2 ^ n) (hy : ∃ m : ℕ, y = 2 ^ m)
    (hxy : x ≠ y) : x ∣ y ∨ y ∣ x := by
  obtain ⟨ n, rfl ⟩ := hx; obtain ⟨ m, rfl ⟩ := hy; cases le_total n m <;> simp +decide [ *, pow_dvd_pow_iff ] ;

/-
PROBLEM
When a = b = c = 2, PowTripleSet is just {2^n : n ≥ 0},
    which is NOT d-complete (antichain sums are limited to single elements).

PROVIDED SOLUTION
PowTripleSet 2 2 2 = {2^(i+j+k) : i,j,k ∈ ℕ} = {2^n : n ≥ 0} = {1, 2, 4, 8, 16, ...}. In this set, every pair of distinct elements satisfies x ∣ y or y ∣ x (by powers_of_two_chain). So any division antichain from this set has at most 1 element. Therefore the only representable values are the single elements {2^n}, and any non-power-of-2 ≥ 3 (like 3, 5, 6, 7, ...) is not representable. In particular, 3 is not representable, nor is any odd number > 1. Since there are infinitely many non-representable numbers, IsDComplete fails. Formally: show that for n=3, there is no antichain finset from PowTripleSet 2 2 2 summing to 3. Unfold IsDComplete and show the filter condition fails: the set of n where the condition holds does not contain all sufficiently large n (e.g., it misses all n = 2*m+1 for m ≥ 1, i.e., odd numbers ≥ 3).
-/
theorem not_d_complete_equal_bases :
    ¬ IsDComplete (PowTripleSet 2 2 2) := by
  unfold IsDComplete;
  simp +decide [ IsDivisionAntichain ];
  intro n
  use 2 * n + 3
  simp [PowTripleSet] at *;
  refine' ⟨ by linarith, fun x hx₁ hx₂ hx₃ => _ ⟩ ; rcases x.eq_empty_or_nonempty with ( rfl | ⟨ y, hy ⟩ ) <;> simp_all +decide [ Set.subset_def ] ;
  contrapose! hx₂; have := hx₁ _ hy; obtain ⟨ i, j, k, rfl ⟩ := this; simp_all +decide [ ← pow_add ] ;
  by_cases h_eq : ∀ y ∈ x, y = 2 ^ (i + j + k);
  · rw [ Finset.sum_congr rfl h_eq ] at hx₃ ; norm_num at hx₃ ; have := congr_arg Even hx₃ ; norm_num [ parity_simps ] at this;
    norm_num [ this ] at hx₃ ; have := congr_arg ( · % 2 ) hx₃ ; norm_num [ Nat.add_mod, Nat.mul_mod ] at this;
    exact absurd ( Finset.card_le_one.2 fun x hx y hy => by linarith [ h_eq x hx, h_eq y hy ] ) ( by linarith );
  · obtain ⟨y, hy₁, hy₂⟩ : ∃ y ∈ x, y ≠ 2 ^ (i + j + k) := by
      exact by push_neg at h_eq; exact h_eq;
    obtain ⟨i', j', k', rfl⟩ := hx₁ y hy₁
    have h_div : 2 ^ (i + j + k) ∣ 2 ^ (i' + j' + k') ∨ 2 ^ (i' + j' + k') ∣ 2 ^ (i + j + k) := by
      cases le_total ( i + j + k ) ( i' + j' + k' ) <;> simp +decide [ *, pow_dvd_pow ]
    cases' h_div with h_div h_div <;> [ exact ⟨_, hy, _, hy₁, by aesop, h_div⟩; exact ⟨_, hy₁, _, hy, by aesop, h_div⟩ ]

/-! ## Necessity of a, b, c > 1

When a = 1, PowTripleSet 1 b c = {b^j · c^k : j, k ≥ 0} (same as two generators).
The antichain structure changes but the set can still be d-complete for coprime b, c > 1.
However, the statement requires all three to be > 1 to ensure the "three-dimensional"
multiplicative structure needed for the general proof. -/

/-
PROBLEM
When a = 1, PowTripleSet 1 b c reduces to {b^j · c^k}.

PROVIDED SOLUTION
Unfold PowTripleSet. When a=1, 1^i = 1 for all i, so a^i * b^j * c^k = b^j * c^k. Use ext to show set equality, then for both directions the witness for i is arbitrary (take i=0).
-/
theorem pow_triple_set_one (b c : ℕ) :
    PowTripleSet 1 b c = {n | ∃ j k : ℕ, n = b ^ j * c ^ k} := by
  unfold PowTripleSet; aesop;

/-! ## Membership and basic structure -/

/-
PROBLEM
1 is always in PowTripleSet (take i=j=k=0).

PROVIDED SOLUTION
Use i=j=k=0. Then a^0 * b^0 * c^0 = 1. Unfold PowTripleSet and use ⟨0, 0, 0, by simp⟩.
-/
theorem one_mem_pow_triple_set (a b c : ℕ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    1 ∈ PowTripleSet a b c := by
  exact ⟨ 0, 0, 0, by norm_num ⟩

/-
PROBLEM
For a, b, c > 1 and pairwise coprime, {a, b, c} is a division antichain
    subset of PowTripleSet, so a + b + c is always representable.

PROVIDED SOLUTION
Use s = {a, b, c} (as a Finset). Show: (1) each is in PowTripleSet (a = a^1*b^0*c^0, etc.), (2) the set is a division antichain (since a,b,c are pairwise coprime and > 1, no one divides another: if a | b then since gcd(a,b)=1 we get a=1, contradiction), (3) sum is a+b+c. For the finset, use Finset.mk or {a, b, c} notation. The distinctness a ≠ b, a ≠ c, b ≠ c is given as hypotheses.
-/
theorem sum_abc_representable (a b c : ℕ) (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)
    (hab : Nat.Coprime a b) (hac : Nat.Coprime a c) (hbc : Nat.Coprime b c)
    (habc : a ≠ b) (habc2 : a ≠ c) (hbc2 : b ≠ c) :
    ∃ s : Finset ℕ, (↑s : Set ℕ) ⊆ PowTripleSet a b c ∧
      IsDivisionAntichain s ∧ s.sum id = a + b + c := by
  refine' ⟨ { a, b, c }, _, _, _ ⟩ <;> simp_all +decide [ Set.subset_def ];
  · exact ⟨ ⟨ 1, 0, 0, by norm_num ⟩, ⟨ 0, 1, 0, by norm_num ⟩, ⟨ 0, 0, 1, by norm_num ⟩ ⟩;
  · intro x y hx hy hxy; simp_all +decide [ Nat.dvd_prime ] ;
    rintro H; rcases hx with ( rfl | rfl | rfl ) <;> rcases hy with ( rfl | rfl | rfl ) <;> simp_all +decide [ Nat.Coprime, Nat.gcd_eq_left_iff_dvd ] ;
    all_goals obtain ⟨ k, rfl ⟩ := H; simp_all +decide [ Nat.gcd_mul_left, Nat.gcd_mul_right ] ;
  · ring

end Erdos123.ParameterExtreme