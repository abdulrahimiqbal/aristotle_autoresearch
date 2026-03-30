/-
# Infrastructure for proving d-completeness

This file builds the key infrastructure needed for the main theorem.
The proof strategy is based on the observation that same-degree elements
form antichains, and their subset sums eventually cover all residues
and sufficiently dense intervals.
-/

import Mathlib

noncomputable section

namespace Erdos123.Infra

open Filter Finset
open scoped BigOperators

def PowTripleSet (a b c : ℕ) : Set ℕ :=
  {n | ∃ i j k : ℕ, n = a ^ i * b ^ j * c ^ k}

def IsDivisionAntichain (s : Finset ℕ) : Prop :=
  ∀ ⦃x y : ℕ⦄, x ∈ s → y ∈ s → x ≠ y → ¬ x ∣ y

def IsDComplete (A : Set ℕ) : Prop :=
  ∀ᶠ n : ℕ in atTop, ∃ s : Finset ℕ,
    (↑s : Set ℕ) ⊆ A ∧ IsDivisionAntichain s ∧ s.sum id = n

def PairwiseCoprime3 (a b c : ℕ) : Prop :=
  Nat.Coprime a b ∧ Nat.Coprime a c ∧ Nat.Coprime b c

/-- The set of degree-d elements: {a^i * b^j * c^k : i+j+k = d} -/
def degreeSet (a b c d : ℕ) : Finset ℕ :=
  (Finset.Icc 0 d ×ˢ Finset.Icc 0 d ×ˢ Finset.Icc 0 d).filter
    (fun p => p.1 + p.2.1 + p.2.2 = d) |>.image
    (fun p => a ^ p.1 * b ^ p.2.1 * c ^ p.2.2)

/-
PROBLEM
Every element of degreeSet is in PowTripleSet.

PROVIDED SOLUTION
Unfold degreeSet and PowTripleSet. Each element of degreeSet is a^i * b^j * c^k for some i,j,k with i+j+k=d, which is clearly in PowTripleSet. Use intro/simp/aesop on the membership condition.
-/
theorem degreeSet_subset_powTripleSet (a b c d : ℕ) :
    ↑(degreeSet a b c d) ⊆ PowTripleSet a b c := by
  grind +locals

/-
PROBLEM
Elements in degreeSet with distinct exponent triples have
    a divisibility relation only if the exponent triples are equal
    (when a,b,c are pairwise coprime and > 1). This makes degreeSet
    a division antichain.

PROVIDED SOLUTION
Unfold IsDivisionAntichain and degreeSet. Take x, y in the image. They come from triples (i1,j1,k1) and (i2,j2,k2) with sums = d. If x ≠ y and x ∣ y, then by coprimality of a,b,c, we get i1 ≤ i2, j1 ≤ j2, k1 ≤ k2. Combined with equal sums = d, this forces equality of triples, hence x = y, contradiction. Use the same_degree_antichain result or reprove the coprimality argument inline.
-/
theorem degreeSet_is_antichain (a b c d : ℕ) (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)
    (hab : Nat.Coprime a b) (hac : Nat.Coprime a c) (hbc : Nat.Coprime b c) :
    IsDivisionAntichain (degreeSet a b c d) := by
  intros x y hx hy hxy;
  obtain ⟨i₁, j₁, k₁, hi₁⟩ : ∃ i j k : ℕ, x = a ^ i * b ^ j * c ^ k ∧ i + j + k = d := by
    unfold degreeSet at hx; aesop;
  obtain ⟨i₂, j₂, k₂, hi₂⟩ : ∃ i j k : ℕ, y = a ^ i * b ^ j * c ^ k ∧ i + j + k = d := by
    unfold degreeSet at hy; aesop;
  have h_div : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ → i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ := by
    intro h_div
    have h_div_a : a ^ i₁ ∣ a ^ i₂ := by
      have h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ := by
        exact dvd_trans ( dvd_mul_of_dvd_left ( dvd_mul_right _ _ ) _ ) h_div;
      exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( a ^ i₁ ) ( b ^ j₂ * c ^ k₂ ) from Nat.Coprime.mul_right ( Nat.Coprime.pow _ _ <| by aesop ) ( Nat.Coprime.pow _ _ <| by aesop ) ) <| by simpa only [ mul_assoc ] using h_div_a )
    have h_div_b : b ^ j₁ ∣ b ^ j₂ := by
      have h_div_b : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ := by
        exact dvd_trans ( dvd_mul_of_dvd_left ( dvd_mul_left _ _ ) _ ) h_div;
      have h_div_b : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ := by
        exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( b ^ j₁ ) ( c ^ k₂ ) from Nat.Coprime.pow _ _ <| by aesop ) h_div_b );
      exact ( Nat.Coprime.dvd_of_dvd_mul_left ( show Nat.Coprime ( b ^ j₁ ) ( a ^ i₂ ) from Nat.Coprime.pow _ _ <| hab.symm ) h_div_b )
    have h_div_c : c ^ k₁ ∣ c ^ k₂ := by
      have h_div_c : c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ := by
        exact dvd_trans ( dvd_mul_left _ _ ) h_div;
      refine' Nat.Coprime.dvd_of_dvd_mul_left _ h_div_c;
      exact Nat.Coprime.mul_right ( Nat.Coprime.pow _ _ <| by simpa [ Nat.coprime_comm ] using hac ) ( Nat.Coprime.pow _ _ <| by simpa [ Nat.coprime_comm ] using hbc );
    exact ⟨ Nat.le_of_not_lt fun h => Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans ha ) _ ) ( pow_lt_pow_right₀ ha h ) h_div_a, Nat.le_of_not_lt fun h => Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans hb ) _ ) ( pow_lt_pow_right₀ hb h ) h_div_b, Nat.le_of_not_lt fun h => Nat.not_dvd_of_pos_of_lt ( pow_pos ( zero_lt_one.trans hc ) _ ) ( pow_lt_pow_right₀ hc h ) h_div_c ⟩;
  lia

/-
PROBLEM
The number of elements in degreeSet d is (d+1)(d+2)/2 when the
    map from exponent triples to values is injective (which holds for
    pairwise coprime a,b,c > 1).

PROVIDED SOLUTION
The exponent triples (i,j,k) with i+j+k=d biject with pairs (i,j) where i+j ≤ d (setting k=d-i-j). There are (d+1)(d+2)/2 such pairs (a standard combinatorial identity). The image map is injective because distinct triples give distinct values (by the coprimality/unique factorization argument). So the card of the image equals the card of the domain = (d+1)(d+2)/2. The injectivity follows from the same argument as same_degree_antichain: if a^i1*b^j1*c^k1 = a^i2*b^j2*c^k2 with i1+j1+k1 = i2+j2+k2 = d, then by the divisibility-implies-equality argument we get (i1,j1,k1) = (i2,j2,k2).
-/
theorem degreeSet_card (a b c d : ℕ) (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)
    (hab : Nat.Coprime a b) (hac : Nat.Coprime a c) (hbc : Nat.Coprime b c) :
    (degreeSet a b c d).card = (d + 1) * (d + 2) / 2 := by
  -- The set of triples (i, j, k) where i + j + k = d is equivalent to the set of pairs (i, j) where i + j ≤ d.
  have h_triples_to_pairs : Finset.filter (fun p => p.1 + p.2.1 + p.2.2 = d) (Finset.Icc 0 d ×ˢ Finset.Icc 0 d ×ˢ Finset.Icc 0 d) = Finset.biUnion (Finset.range (d + 1)) (fun i => Finset.image (fun j => (i, j, d - i - j)) (Finset.Icc 0 (d - i))) := by
    ext ⟨i, j, k⟩; simp [Finset.mem_biUnion, Finset.mem_image];
    omega;
  -- The function $f(i, j, k) = a^i * b^j * c^k$ is injective on the set of triples $(i, j, k)$ with $i + j + k = d$.
  have h_inj : ∀ i j k i' j' k' : ℕ, i + j + k = d → i' + j' + k' = d → a^i * b^j * c^k = a^i' * b^j' * c^k' → i = i' ∧ j = j' ∧ k = k' := by
    intro i j k i' j' k' hi hj h_eq
    have h_div : a^i * b^j * c^k = a^i' * b^j' * c^k' → i = i' ∧ j = j' ∧ k = k' := by
      intro h_eq
      have h_div_a : a ^ i = a ^ i' := by
        apply_mod_cast Nat.dvd_antisymm;
        · have h_div_a : a ^ i ∣ a ^ i' * b ^ j' * c ^ k' := by
            exact h_eq ▸ dvd_mul_of_dvd_left ( dvd_mul_right _ _ ) _;
          have h_div_a : a ^ i ∣ a ^ i' * b ^ j' * c ^ k' → a ^ i ∣ a ^ i' := by
            intro h_div_a
            have h_coprime : Nat.Coprime (a ^ i) (b ^ j' * c ^ k') := by
              apply_rules [ Nat.Coprime.mul_right, Nat.Coprime.pow ]
            exact h_coprime.dvd_of_dvd_mul_right <| by simpa only [ mul_assoc ] using h_div_a;
          exact h_div_a ‹_›;
        · have h_div_a : a ^ i' ∣ a ^ i * b ^ j * c ^ k := by
            exact h_eq.symm ▸ dvd_mul_of_dvd_left ( dvd_mul_right _ _ ) _;
          have h_coprime_a : Nat.Coprime (a ^ i') (b ^ j * c ^ k) := by
            apply_rules [ Nat.Coprime.mul_right, Nat.Coprime.pow ];
          exact h_coprime_a.dvd_of_dvd_mul_right <| by simpa only [ mul_assoc ] using h_div_a;
      have h_div_b : b ^ j = b ^ j' := by
        have h_div_b : b ^ j * c ^ k = b ^ j' * c ^ k' := by
          simp_all +decide [ mul_assoc, ne_of_gt ( zero_lt_one.trans ha ), ne_of_gt ( zero_lt_one.trans hb ), ne_of_gt ( zero_lt_one.trans hc ) ];
        apply_mod_cast Nat.dvd_antisymm;
        · exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( b ^ j ) ( c ^ k' ) from Nat.Coprime.pow _ _ <| by aesop ) ) <| h_div_b ▸ dvd_mul_right _ _;
        · exact Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( b ^ j' ) ( c ^ k ) from Nat.Coprime.pow _ _ <| by aesop ) <| h_div_b.symm ▸ dvd_mul_right _ _
      have h_div_c : c ^ k = c ^ k' := by
        aesop
      exact ⟨by
      exact Nat.pow_right_injective ha h_div_a, by
        exact Nat.pow_right_injective hb h_div_b, by
        exact Nat.pow_right_injective hc h_div_c⟩;
    exact h_div h_eq;
  -- The cardinality of the image of an injective function is equal to the cardinality of its domain.
  have h_card_image : Finset.card (Finset.image (fun p => a^p.1 * b^p.2.1 * c^p.2.2) (Finset.filter (fun p => p.1 + p.2.1 + p.2.2 = d) (Finset.Icc 0 d ×ˢ Finset.Icc 0 d ×ˢ Finset.Icc 0 d))) = Finset.card (Finset.filter (fun p => p.1 + p.2.1 + p.2.2 = d) (Finset.Icc 0 d ×ˢ Finset.Icc 0 d ×ˢ Finset.Icc 0 d)) := by
    exact Finset.card_image_of_injOn fun p hp q hq h => by specialize h_inj p.1 p.2.1 p.2.2 q.1 q.2.1 q.2.2; aesop;
  convert h_card_image using 1;
  rw [ h_triples_to_pairs, Finset.card_biUnion ];
  · norm_num [ Finset.card_image_of_injective, Function.Injective ];
    exact Nat.div_eq_of_eq_mul_left zero_lt_two <| Nat.recOn d ( by norm_num ) fun n ih => by cases n <;> simp +decide [ Finset.sum_range_succ', Nat.mul_succ ] at * ; linarith;
  · intros i hi j hj hij; simp [Finset.disjoint_left, Finset.mem_image];
    grind

end Erdos123.Infra