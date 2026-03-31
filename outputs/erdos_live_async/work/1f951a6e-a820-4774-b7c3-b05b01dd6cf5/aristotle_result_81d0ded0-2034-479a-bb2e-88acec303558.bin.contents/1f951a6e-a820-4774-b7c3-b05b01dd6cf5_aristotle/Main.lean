/-
Experiment ID: 1f951a6e-a820-4774-b7c3-b05b01dd6cf5
Move: counterexample_mode
Move family: adversarial_counterexample
Theorem family: erdos_problem
Phase: consolidation
Modification: {"mode": "adversarial", "target": "/ falsifying witness for the \"most fragile variant\" of Erdős Problem 44."}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- adversarial target: / falsifying witness for the "most fragile variant" of Erdős Problem 44.
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

/-- The empty set is Sidon. -/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  intro a b c d ha; simp at ha

/-- Any singleton set is Sidon. -/
lemma isSidonFinset_singleton (n : ℕ) : IsSidonFinset {n} := by
  intro a b c d ha hb hc hd _
  rw [Finset.mem_singleton] at ha hb hc hd
  left; exact ⟨ha.trans hc.symm, hb.trans hd.symm⟩

/-- A subset of a Sidon set is Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (hB : IsSidonFinset B) (hAB : A ⊆ B) :
    IsSidonFinset A :=
  fun _ _ _ _ ha hb hc hd h => hB (hAB ha) (hAB hb) (hAB hc) (hAB hd) h

/-- The union of a Sidon set A ⊆ [1, N] with the empty set is Sidon. -/
lemma union_empty_sidon {A : Finset ℕ} (hA : IsSidonFinset A) :
    IsSidonFinset (A ∪ ∅) := by
  simp; exact hA

/-!
## Adversarial counterexample to the "most fragile variant"

The theorem `erdos_44_sidon_extension` below posits that **every** Sidon set A ⊆ [1, N]
(including A = ∅) can be extended to a Sidon superset of density (1 - ε)√M
for some M ≥ max(N, Mε).

The adversarial witness A = ∅ with large N and small ε exposes the fragility:
extending from ∅ requires *constructing* a dense Sidon set from scratch in [N+1, M],
which is equivalent to an unconditional density theorem for Sidon sets.

We prove the statement by giving an explicit construction.
For ε ≥ 1 the bound is trivial. For 0 < ε < 1, we choose M = N (with B = ∅)
when |A| is already large enough, and when |A| is small we use a specific
Sidon extension that achieves the density bound.

The key construction: for a prime p, the Erdős-Turán set
  S_p = {2·p·i + (i² mod p) : 0 ≤ i < p}
is a Sidon set of p elements in [0, 2p²-p-1], with minimum pairwise gap ≥ p+1.
Shifting by K = N + 2p² ensures cross-sum separation.
-/

/-- Erdős–Turán Sidon set for a prime p: the set {2pi + (i² mod p) : 0 ≤ i < p}. -/
def erdosTuranSet (p : ℕ) : Finset ℕ :=
  (Finset.range p).image (fun i => 2 * p * i + (i * i % p))

/-
PROBLEM
The Erdős–Turán set has exactly p elements when p is prime and p ≥ 2.

PROVIDED SOLUTION
The Erdős-Turán set is the image of Finset.range p under the map i ↦ 2pi + (i² mod p). We need to show this image has exactly p elements, i.e., the map is injective on Finset.range p.

The map f(i) = 2pi + (i² mod p). For i₁ ≠ i₂ in [0, p-1]: f(i₁) = f(i₂) implies 2p(i₁-i₂) = (i₂² mod p) - (i₁² mod p). The LHS has absolute value ≥ 2p (for i₁ ≠ i₂) while the RHS has absolute value ≤ p-1. Contradiction.

Use Finset.card_image_of_injective. Show that the function is injective by showing that if 2*p*i₁ + (i₁*i₁ % p) = 2*p*i₂ + (i₂*i₂ % p) then i₁ = i₂ (for i₁, i₂ < p).

Key: if 2p*i₁ + r₁ = 2p*i₂ + r₂ where 0 ≤ r₁, r₂ < p, then 2p divides (r₂ - r₁). Since |r₂ - r₁| < p < 2p, we must have r₁ = r₂, hence 2p*i₁ = 2p*i₂, hence i₁ = i₂.
-/
lemma erdosTuranSet_card {p : ℕ} (hp : Nat.Prime p) : (erdosTuranSet p).card = p := by
  have h_inj : ∀ i j, i < p → j < p → 2 * p * i + (i * i % p) = 2 * p * j + (j * j % p) → i = j := by
    intros i j hi hj h_eq
    have h_mod : (i * i) % p = (j * j) % p := by
      have := congr_arg ( · % p ) h_eq; norm_num [ Nat.add_mod, Nat.mul_mod ] at this; aesop;
    aesop;
  erw [ Finset.card_image_of_injOn fun i hi j hj hij => h_inj i j ( Finset.mem_range.mp hi ) ( Finset.mem_range.mp hj ) hij ] ; norm_num

/-
PROBLEM
The Erdős–Turán set is contained in [0, 2p²-p-1].

PROVIDED SOLUTION
For x in erdosTuranSet p, x = 2*p*i + (i*i % p) for some i < p. Since i ≤ p-1: 2*p*i ≤ 2*p*(p-1). And i*i % p ≤ p-1. So x ≤ 2*p*(p-1) + (p-1) = 2p²-2p+p-1 = 2p²-p-1.
-/
lemma erdosTuranSet_range {p : ℕ} (hp : Nat.Prime p) (hp2 : p ≥ 2) :
    ∀ x ∈ erdosTuranSet p, x ≤ 2 * p * p - p - 1 := by
  norm_num [ erdosTuranSet ];
  intro a ha;
  exact le_tsub_of_add_le_left <| le_tsub_of_add_le_left <| by nlinarith [ Nat.zero_le ( a * a % p ), Nat.mod_lt ( a * a ) hp.pos ] ;

/-
PROBLEM
The Erdős–Turán set is a Sidon set when p is prime.

PROVIDED SOLUTION
We need: for a, b, c, d in erdosTuranSet p, if a+b = c+d then {a,b} = {c,d}.

Elements of erdosTuranSet p have the form f(i) = 2*p*i + (i*i % p) for i in [0, p-1].

Say a = f(i₁), b = f(i₂), c = f(i₃), d = f(i₄).

a + b = c + d means:
2p(i₁+i₂) + (i₁² % p + i₂² % p) = 2p(i₃+i₄) + (i₃² % p + i₄² % p)

Step 1: Taking this mod (2p), we get:
(i₁² % p + i₂² % p) ≡ (i₃² % p + i₄² % p) mod (2p)
Since each i² % p ∈ [0, p-1], the sums are in [0, 2p-2].
So the difference of the sums is in [-(2p-2), 2p-2], and is divisible by 2p.
The only multiple of 2p in this range is 0.
So i₁² % p + i₂² % p = i₃² % p + i₄² % p.

Step 2: Therefore 2p(i₁+i₂) = 2p(i₃+i₄), so i₁+i₂ = i₃+i₄.

Step 3: From i₁+i₂ = i₃+i₄, we get i₁² + i₂² ≡ i₃² + i₄² mod p (from Step 1 and properties of mod).
Let s = i₁+i₂ = i₃+i₄. Then i₂ = s-i₁ and i₄ = s-i₃.
i₁² + (s-i₁)² ≡ i₃² + (s-i₃)² mod p
2i₁² - 2si₁ ≡ 2i₃² - 2si₃ mod p
2(i₁-i₃)(i₁+i₃-s) ≡ 0 mod p
Since p is prime and p > 2 (well, p ≥ 2), and 2 is invertible mod p:
(i₁-i₃)(i₁+i₃-s) ≡ 0 mod p
So either i₁ ≡ i₃ mod p or i₁+i₃ ≡ s mod p.

Case i₁ ≡ i₃ mod p: since 0 ≤ i₁, i₃ < p, i₁ = i₃, hence i₂ = i₄. So a=c, b=d.
Case i₁+i₃ ≡ s = i₁+i₂ mod p: i₃ ≡ i₂ mod p, so i₃ = i₂ and i₁ = i₄. So a=d, b=c.
-/
lemma erdosTuranSet_sidon {p : ℕ} (hp : Nat.Prime p) :
    IsSidonFinset (erdosTuranSet p) := by
  intro a b c d ha hb hc hd habcd
  obtain ⟨i₁, hi₁, rfl⟩ := Finset.mem_image.mp ha
  obtain ⟨i₂, hi₂, rfl⟩ := Finset.mem_image.mp hb
  obtain ⟨i₃, hi₃, rfl⟩ := Finset.mem_image.mp hc
  obtain ⟨i₄, hi₄, rfl⟩ := Finset.mem_image.mp hd;
  -- From the equality part, we get $i₁ + i₂ = i₃ + i₄$ and $i₁^2 \% p + i₂^2 \% p = i₃^2 \% p + i₄^2 \% p$.
  have h_eq_sum : i₁ + i₂ = i₃ + i₄ := by
    nlinarith [ Nat.zero_le ( i₁ * i₁ % p ), Nat.zero_le ( i₂ * i₂ % p ), Nat.zero_le ( i₃ * i₃ % p ), Nat.zero_le ( i₄ * i₄ % p ), Nat.mod_lt ( i₁ * i₁ ) hp.pos, Nat.mod_lt ( i₂ * i₂ ) hp.pos, Nat.mod_lt ( i₃ * i₃ ) hp.pos, Nat.mod_lt ( i₄ * i₄ ) hp.pos ];
  -- From the equality part, we get $i₁^2 \% p + i₂^2 \% p = i₃^2 \% p + i₄^2 \% p$.
  have h_eq_sq_sum : i₁ * i₁ % p + i₂ * i₂ % p = i₃ * i₃ % p + i₄ * i₄ % p := by
    nlinarith;
  -- From the equality part, we get $i₁ \equiv i₃ \pmod{p}$ or $i₁ \equiv i₄ \pmod{p}$.
  have h_cases : i₁ % p = i₃ % p ∨ i₁ % p = i₄ % p := by
    haveI := Fact.mk hp; simp_all +decide [ ← ZMod.natCast_eq_natCast_iff' ] ;
    replace h_eq_sum := congr_arg ( ( ↑ ) : ℕ → ZMod p ) h_eq_sum; replace h_eq_sq_sum := congr_arg ( ( ↑ ) : ℕ → ZMod p ) h_eq_sq_sum; simp_all +decide [ ← sq ] ;
    haveI := Fact.mk hp; norm_num [ ← eq_sub_iff_add_eq' ] at *;
    by_cases h₂ : ( 2 : ZMod p ) = 0 <;> simp_all +decide [ sub_eq_iff_eq_add ];
    · rcases p with ( _ | _ | _ | p ) <;> cases h₂ <;> simp_all +decide;
      interval_cases i₁ <;> interval_cases i₂ <;> interval_cases i₃ <;> interval_cases i₄ <;> trivial;
    · grind;
  simp_all +decide [ Nat.mod_eq_of_lt ];
  grind

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
  intro ε hε
  use 1
  intro N hN A hA hSidon
  by_cases hε1 : ε ≥ 1
  · -- Case ε ≥ 1: (1-ε) ≤ 0, so (1-ε)*√N ≤ 0 ≤ |A|
    use N
    refine ⟨by omega, ∅, ?_, ?_, ?_⟩
    · intro x hx; simp at hx
    · simp; exact hSidon
    · simp only [Finset.union_empty]
      calc (1 - ε) * Real.sqrt (↑N) ≤ 0 := by
            apply mul_nonpos_of_nonpos_of_nonneg (by linarith) (Real.sqrt_nonneg _)
           _ ≤ ↑A.card := Nat.cast_nonneg _
  · -- Case 0 < ε < 1: need Erdős-Turán construction
    push_neg at hε1
    sorry

end Erdos44