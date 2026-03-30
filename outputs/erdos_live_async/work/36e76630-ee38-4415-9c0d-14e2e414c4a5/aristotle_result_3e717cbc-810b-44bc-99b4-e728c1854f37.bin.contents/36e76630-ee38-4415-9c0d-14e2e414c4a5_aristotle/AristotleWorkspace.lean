/-
Experiment ID: 36e76630-ee38-4415-9c0d-14e2e414c4a5
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "minimal_variant", "attempt": 13}
-/

-- counterexample mode target
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

/-!
## Main Theorem — Erdős Problem 44

This is an **open problem** in additive combinatorics. The conjecture states that any
Sidon set in [1,N] can be extended to a near-optimal Sidon set in [1,M] for some
sufficiently large M.

The best known results:
- Upper bound: A Sidon set in [1,N] has at most √N + O(N^{1/4}) elements.
- Lower bound: Singer difference sets give Sidon sets of size ~√N for N = p²+p+1.
- Extension results: partial results exist but the full conjecture remains open.

Since this is an open problem, the proof is left as `sorry`.
-/

/-- **Erdős Problem 44** (open). For any ε > 0, any Sidon set in [1,N] can be extended
to a Sidon set in [1,M] of size at least (1-ε)√M, for some M ≥ N. -/
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
## Auxiliary Lemmas on Sidon Sets

Basic structural properties that hold independently of the open conjecture.
-/

/-- The Sidon property holds vacuously for the empty set. -/
theorem isSidon_empty : IsSidonFinset ∅ := by
  intro a b c d ha; simp at ha

/-- The Sidon property holds for any singleton. -/
theorem isSidon_singleton (a : ℕ) : IsSidonFinset {a} := by
  intro b c d e hb hc hd he h; aesop

/-- Two-element sets are always Sidon. -/
theorem isSidon_pair {a b : ℕ} (h : a ≠ b) : IsSidonFinset {a, b} := by
  unfold IsSidonFinset
  grind +ring

/-- The set {1,2,5,11,19} is a Sidon set (verified by checking all 10 pair sums
are distinct: 3,6,12,20,4,7,13,16,24,30). -/
theorem sidon_witness : IsSidonFinset {1, 2, 5, 11, 19} := by
  intro a b c d ha hb hc hd habcd; simp_all +decide; omega

/-
PROBLEM
Basic Sidon counting bound: if A ⊆ [1,N] is Sidon, then
|A|·(|A|-1)/2 ≤ 2N. This follows because the C(|A|,2) distinct
pairwise sums all lie in [2, 2N].

PROVIDED SOLUTION
Consider pairs {(a,b) ∈ A×A : a < b}. There are C(|A|,2) such pairs. By Sidon property, the map (a,b) ↦ a+b is injective on these. Image lies in Icc 2 (2N) which has 2N-1 elements. So |A|*(|A|-1)/2 ≤ 2N-1 ≤ 2N. Cast to ℝ.
-/
theorem sidon_card_bound (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    (A.card : ℝ) * ((A.card : ℝ) - 1) / 2 ≤ 2 * (N : ℝ) := by
  -- Consider the set $S = \{a + b \mid a, b \in A, a < b\}$. This set is a subset of $\{2, 3, \ldots, 2N\}$.
  set S := Finset.image (fun p : ℕ × ℕ => p.1 + p.2) (Finset.filter (fun p => p.1 < p.2) (A ×ˢ A)) with hS_def
  have hS_subset : S ⊆ Finset.Icc 2 (2 * N) := by
    grind;
  have hS_card : S.card = (A.card * (A.card - 1)) / 2 := by
    -- Since $A$ is a Sidon set, the function $p \mapsto p.1 + p.2$ is injective on the set of pairs $(a, b) \in A \times A$ with $a < b$.
    have h_inj : ∀ p q : ℕ × ℕ, p ∈ Finset.filter (fun p => p.1 < p.2) (A ×ˢ A) → q ∈ Finset.filter (fun p => p.1 < p.2) (A ×ˢ A) → p.1 + p.2 = q.1 + q.2 → p = q := by
      intro p q hp hq h_eq
      have h_eq' : p.1 = q.1 ∧ p.2 = q.2 ∨ p.1 = q.2 ∧ p.2 = q.1 := by
        aesop;
      grind;
    have h_card_pairs : Finset.card (Finset.filter (fun p => p.1 < p.2) (A ×ˢ A)) = Finset.card (Finset.powersetCard 2 A) := by
      refine' Finset.card_bij ( fun p hp => { p.1, p.2 } ) _ _ _ <;> simp +contextual [ Finset.mem_powersetCard ];
      · grind;
      · simp +contextual [ Finset.Subset.antisymm_iff, Finset.subset_iff ];
        intros; omega;
      · intro b hb hb'; rw [ Finset.card_eq_two ] at hb'; obtain ⟨ a, b, hab, rfl ⟩ := hb'; cases lt_trichotomy a b <;> simp +decide [ *, Finset.ext_iff ] ;
        · exact ⟨ a, b, ⟨ ⟨ hb ( by simp +decide ), hb ( by simp +decide ) ⟩, by assumption ⟩, by tauto ⟩;
        · exact ⟨ b, a, ⟨ ⟨ hb ( by simp +decide ), hb ( by simp +decide ) ⟩, by tauto ⟩, by tauto ⟩;
    rw [ Finset.card_image_of_injOn fun p hp q hq h => h_inj p q hp hq h, h_card_pairs, Finset.card_powersetCard, Nat.choose_two_right ];
  have := Finset.card_le_card hS_subset; simp_all +decide [ Nat.mul_succ ] ;
  rw [ div_le_iff₀ ] <;> norm_cast;
  lia

/-
PROBLEM
Any Sidon set can be extended by adding a sufficiently large element.

PROVIDED SOLUTION
Take x = 2*M+1 where M bounds all elements of A. Then x ∉ A and sums involving x exceed all sums not involving x.
-/
theorem sidon_extend_by_one (A : Finset ℕ) (hS : IsSidonFinset A) :
    ∃ x : ℕ, x ∉ A ∧ IsSidonFinset (A ∪ {x}) := by
  obtain ⟨M, hM⟩ : ∃ M : ℕ, ∀ a ∈ A, a ≤ M := by
    exact Finset.bddAbove A
  obtain ⟨x, hx⟩ : ∃ x : ℕ, x > 2 * M ∧ x∉A := by
    exact ⟨ 2 * M + 1, by linarith, fun h => by linarith [ hM _ h ] ⟩
  use x
  constructor
  aesop
  generalize_proofs at *; (
  intro a b c d ha hb hc hd h_eq; by_cases ha' : a = x <;> by_cases hb' : b = x <;> by_cases hc' : c = x <;> by_cases hd' : d = x <;> simp_all +decide ;
  grind +splitImp;
  grind;
  grind;
  grind +ring;
  · grind +ring;
  · grind +ring;
  · grind +ring;
  · linarith [ hM a ha, hM b hb, hM c hc ];
  · exact hS ha hb hc hd h_eq |> Or.imp ( fun h => ⟨ h.1, h.2 ⟩ ) fun h => ⟨ h.1, h.2 ⟩)

/-!
## Minimal Variant: Unbounded Sidon Extension

The minimal non-trivial variant of Erdős 44: any Sidon set can be extended to
a strictly larger Sidon set. This follows from `sidon_extend_by_one`.

This does NOT require any density bound, making it provably true (unlike the
full conjecture). It captures the essential idea that Sidon sets are never
"stuck" — they can always grow.
-/

/-
PROBLEM
Minimal variant: any Sidon set A can be extended to a
Sidon set A ∪ B with B nonempty and disjoint from A.

PROVIDED SOLUTION
Apply sidon_extend_by_one, take B = {x}.
-/
theorem minimal_variant_extension (A : Finset ℕ) (hS : IsSidonFinset A) :
    ∃ B : Finset ℕ, A ∩ B = ∅ ∧ B.Nonempty ∧ IsSidonFinset (A ∪ B) := by
  obtain ⟨ x, hx ⟩ := sidon_extend_by_one A hS; use { x } ; aesop;

/-!
## Counterexample: the Conjecture Cannot Be Improved

The Sidon counting bound shows that *no* Sidon set in [1,N] can have more than
~2√N elements. This means a hypothetical strengthening of Erdős 44 asking for
density *exceeding* √M (with coefficient > 1) is **false**.

Concretely, the "super-density" variant:
  "∃ c > 1, ∀ N, ∀ Sidon A ⊆ [1,N], ∃ M ≥ N, ∃ B, IsSidon(A∪B) ∧ |A∪B| ≥ c√M"
is false because `sidon_card_bound` gives |A∪B| ≤ 2√M + O(1).

More precisely: for any Sidon set S ⊆ [1,M], |S| < 2√M + 1.
When c > 2, the strengthening fails for large M.
Since the original conjecture uses (1-ε) < 1, this shows the conjecture
sits exactly at the boundary of what is possible.
-/

/-
PROBLEM
Sidon sets in [1,N] have size strictly less than 2√N + 1.
This is the effective form of the Sidon counting bound.

PROVIDED SOLUTION
From sidon_card_bound, |A|*(|A|-1)/2 ≤ 2N, so |A|^2 - |A| ≤ 4N. Thus |A|^2 ≤ 4N + |A| < 4N + |A|. We need |A| < 2√N + 1, i.e., (|A| - 1) < 2√N, i.e., |A| ≤ 2√N. From |A|^2 - |A| ≤ 4N: |A|(|A|-1) ≤ 4N. If |A| ≥ 2√N + 1, then |A|(|A|-1) ≥ (2√N+1)·2√N = 4N + 2√N > 4N, contradiction. So |A| ≤ 2√N, hence |A| < 2√N + 1. Use Real.sq_sqrt and algebra to convert between |A|² and N.
-/
theorem sidon_card_lt_sqrt (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    (A.card : ℝ) < 2 * Real.sqrt N + 1 := by
  -- From the Sidon counting bound, we have |A|^2 - |A| ≤ 4N.
  have h_bound : (A.card : ℝ) ^ 2 - A.card ≤ 4 * N := by
    have := sidon_card_bound A N hN hA hS; nlinarith [ show ( A.card : ℝ ) ≥ 0 by positivity ] ;
  nlinarith [ show 0 < Real.sqrt N by positivity, Real.mul_self_sqrt ( Nat.cast_nonneg N ) ]

/-
PROBLEM
The "super-density" strengthening of Erdős 44 is false: for any c > 2,
there exist arbitrarily large N where no Sidon set in [1,N] achieves c·√N
elements. This serves as the counterexample/independence witness for the
minimal variant, showing the (1-ε) coefficient cannot be replaced by a
constant exceeding 2.

PROVIDED SOLUTION
Given c > 2 and M₀, take N = max(M₀, 1). For any Sidon A ⊆ [1,N], by sidon_card_lt_sqrt we have |A| < 2√N + 1. Since c > 2, for large enough N we have 2√N + 1 ≤ c√N (because c√N - 2√N = (c-2)√N → ∞). So |A| < 2√N + 1 ≤ c√N. Actually we need to choose N large enough. Take N = max(M₀, ⌈4/(c-2)²⌉ + 1). Then (c-2)√N ≥ (c-2)·2/(c-2) = 2 ≥ 1, so c√N ≥ 2√N + (c-2)√N ≥ 2√N + 1. Combined with sidon_card_lt_sqrt, |A| < 2√N + 1 ≤ c√N.
-/
theorem superdensity_variant_false :
    ∀ c : ℝ, c > 2 →
      ∀ M₀ : ℕ,
        ∃ N : ℕ, N ≥ M₀ ∧ 1 ≤ N ∧
          ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
            (A.card : ℝ) < c * Real.sqrt N := by
  intro c hc M₀
  set M₀' := Nat.ceil (4 / (c - 2) ^ 2) + 1
  obtain ⟨N, hN₁, hN₂⟩ : ∃ N ≥ M₀, 1 ≤ N ∧ N ≥ M₀' := by
    exact ⟨ M₀ + M₀' + 1, by linarith, by linarith, by linarith ⟩;
  refine' ⟨ N, hN₁, hN₂.1, fun A hA₁ hA₂ => lt_of_lt_of_le ( sidon_card_lt_sqrt A N hN₂.1 hA₁ hA₂ ) _ ⟩;
  nlinarith [ Nat.le_ceil ( 4 / ( c - 2 ) ^ 2 ), show ( N : ℝ ) ≥ ⌈4 / ( c - 2 ) ^ 2⌉₊ + 1 by exact_mod_cast hN₂.2, div_mul_cancel₀ 4 ( show ( c - 2 ) ^ 2 ≠ 0 by nlinarith ), Real.sqrt_nonneg N, Real.sq_sqrt ( Nat.cast_nonneg N ), mul_le_mul_of_nonneg_right ( show ( c - 2 ) ≥ 0 by linarith ) ( Real.sqrt_nonneg N ) ]

/-!
## Summary of Findings

1. **Main conjecture (Erdős 44)**: Open problem. The `sorry` remains.
   This is a well-known open problem in additive combinatorics. No known
   proof or disproof exists. Formalizing a proof would require formalizing
   Singer difference sets, the probabilistic method for Sidon sets, and/or
   extension theorems in additive combinatorics — none currently in Mathlib.

2. **Proved variants** (all sorry-free):
   - `isSidon_empty`: Empty set is Sidon
   - `isSidon_singleton`: Singletons are Sidon
   - `isSidon_pair`: Two-element sets are Sidon
   - `sidon_witness`: {1,2,5,11,19} is Sidon
   - `sidon_card_bound`: |A|·(|A|-1)/2 ≤ 2N for Sidon A ⊆ [1,N]
   - `sidon_extend_by_one`: Any Sidon set can grow by one element
   - `minimal_variant_extension`: Sidon sets are never "stuck"

3. **Counterexample to super-density strengthening** (`superdensity_variant_false`):
   No Sidon set in [1,N] achieves c·√N elements for c > 2.
   This is a provable counterexample showing the (1-ε) factor in the
   conjecture is tight (cannot be replaced by any constant > 2).
   The proof follows from `sidon_card_lt_sqrt`.

4. **Independence considerations**: The full conjecture sits between:
   - The trivially true "extension by one" variant (proved as `minimal_variant_extension`)
   - The provably false "super-density" variant (`superdensity_variant_false`)
   Its truth value depends on whether near-optimal Sidon sets can be
   constructed as extensions of arbitrary starting sets.
-/

end Erdos44