/-
Counterexample / falsifying witness for the "most fragile variant" of Erdős Problem 44.

The original conjecture (an open problem) claims Sidon sets can always be extended to
achieve density `(1-ε)√M`.  The hard ceiling from the Sidon counting bound is `< 2√M`
(i.e., `√(4M)`).  The "most fragile" natural strengthening replaces `(1-ε)` with `2`,
demanding `2√M ≤ |A ∪ B|`, and this is **provably false** for every Sidon set in `[1,M]`.

We prove:
  1. `sidon_card_sq_lt` : If `A ⊆ [1,N]` is Sidon with `N ≥ 1`, then `A.card² < 4N`.
  2. `sidon_card_lt_two_sqrt` : Consequently `(A.card : ℝ) < 2 * √N`.
  3. `erdos44_strengthened_false` : The strengthened Erdős 44 with constant `2` is false.
-/
import Mathlib

noncomputable section

namespace Erdos44

open Finset
open scoped BigOperators

/-- A finite set of natural numbers is Sidon (B₂) if equal pair sums force the
summands to agree up to reordering. -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ### Sidon counting bound

The standard double-counting argument: the `|A|²` ordered pair sums from `A × A`
each represent at most 2 ordered pairs per unordered pair, so the number of distinct
sums is ≥ `|A|²/2`.  These sums lie in `[2, 2N]` (with `2N - 1` values), giving
`|A|² ≤ 2(2N - 1) < 4N`.
-/

/-- In a Sidon set, for each sum value `s`, the fiber `{(a,b) ∈ A×A : a+b = s}` has
at most 2 elements: the pair `(a,b)` and its reverse `(b,a)`. -/
lemma sidon_fiber_le_two (A : Finset ℕ) (hS : IsSidonFinset A) (s : ℕ) :
    ((A ×ˢ A).filter (fun p => p.1 + p.2 = s)).card ≤ 2 := by
  set S := {p ∈ A ×ˢ A | p.1 + p.2 = s}
  have hSidon : ∀ p q : ℕ × ℕ, p ∈ S → q ∈ S → p = q ∨ p = (q.2, q.1) := by aesop
  by_contra h_contra
  obtain ⟨p, hp, q, hq, hpq⟩ := Finset.two_lt_card.mp (lt_of_not_ge h_contra)
  grind

/-- The image of the sum map on `A × A` is contained in `[2, 2N]` when `A ⊆ [1,N]`. -/
lemma sidon_sum_range (A : Finset ℕ) (N : ℕ) (_hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) :
    (A ×ˢ A).image (fun p : ℕ × ℕ => p.1 + p.2) ⊆ Finset.Icc 2 (2 * N) := by
  exact Finset.image_subset_iff.mpr fun p hp =>
    Finset.mem_Icc.mpr
      ⟨by linarith [Finset.mem_Icc.mp (hA (Finset.mem_product.mp hp |>.1)),
                     Finset.mem_Icc.mp (hA (Finset.mem_product.mp hp |>.2))],
       by linarith [Finset.mem_Icc.mp (hA (Finset.mem_product.mp hp |>.1)),
                     Finset.mem_Icc.mp (hA (Finset.mem_product.mp hp |>.2))]⟩

/-- Core counting bound: `|A|² < 4N` for any Sidon set `A ⊆ [1,N]` with `N ≥ 1`. -/
theorem sidon_card_sq_lt (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    A.card ^ 2 < 4 * N := by
  have h_fiber_le_two : ∀ s ∈ (A ×ˢ A).image (fun p => p.1 + p.2),
      ((A ×ˢ A).filter (fun p => p.1 + p.2 = s)).card ≤ 2 :=
    fun s _ => sidon_fiber_le_two A hS s
  have h_total : (A ×ˢ A).card ≤ 2 * ((A ×ˢ A).image (fun p => p.1 + p.2)).card :=
    card_le_mul_card_image (A ×ˢ A) 2 h_fiber_le_two
  have h_range := sidon_sum_range A N hN hA
  have := Finset.card_mono h_range
  simp_all +decide [sq]
  grind +splitImp

/-- Real-valued form: `|A| < 2√N`. -/
theorem sidon_card_lt_two_sqrt (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    (A.card : ℝ) < 2 * Real.sqrt N := by
  have h_ineq : (A.card : ℝ) ^ 2 < 4 * N := by exact_mod_cast sidon_card_sq_lt A N hN hA hS
  nlinarith [Real.sqrt_nonneg N, Real.sq_sqrt (Nat.cast_nonneg N)]

/-! ### The strengthened variant is false

Replace `(1 - ε)` by `2` in the Erdős 44 conclusion.  For any Sidon set
`S ⊆ [1,M]` we have `|S| < 2√M`, so demanding `2√M ≤ |S|` is impossible.

The density constant `2` is exactly the counting-bound ceiling `√(4M)/√M`.
Pushing the original `(1-ε)` past this value crosses from "open conjecture"
territory into "provably false" territory — making it the **most fragile
observed variant**. -/

/-- The "strengthened Erdős 44" with constant `2` is false: no Sidon set in `[1,M]`
can have `≥ 2√M` elements.  This is the falsifying witness for the most fragile
observed variant — pushing the density constant to the counting-bound ceiling. -/
theorem erdos44_strengthened_false :
    ¬ (∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ N ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            2 * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  simp +zetaDelta at *
  refine' ⟨1, by norm_num, {1}, _, _, _⟩ <;> norm_num
  · exact fun a b c d ha hb hc hd h => by aesop
  · intro x hx y hy h
    have := sidon_card_lt_two_sqrt (insert 1 y) x hx (by
      exact Finset.insert_subset_iff.mpr
        ⟨Finset.mem_Icc.mpr ⟨by linarith, by linarith⟩,
         hy.trans (Finset.Icc_subset_Icc (by linarith) le_rfl)⟩) h
    aesop

/-! ### Explicit small witness

`{1,2,4}` is a Sidon set in `[1,4]` with 3 elements.  The bound gives `3 < 2√4 = 4`.
Any extension of this set to `[1,M]` keeping the Sidon property has `< 2√M` elements,
so the constant `2` is never achieved. -/

/-- `{1,2,4}` is a Sidon set. -/
lemma sidon_example : IsSidonFinset ({1, 2, 4} : Finset ℕ) := by
  intro a b c d ha hb hc hd habcd
  fin_cases ha <;> fin_cases hb <;> fin_cases hc <;> fin_cases hd <;> trivial

end Erdos44
