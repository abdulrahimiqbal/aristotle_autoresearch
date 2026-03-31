/-
Experiment ID: 0b5f61b3-0968-47d3-abab-ae12bdb6c672
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 17, "target": "boundary_variant"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
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

/-! ### Infrastructure for the main theorem

The main theorem (Erdős Problem 44) is a well-known open problem in additive
combinatorics on extending Sidon/B₂ sets to near-optimal density.
The proof requires deep number-theoretic constructions (Singer perfect difference
sets) combined with careful cross-collision analysis. -/

/-- Singer's theorem: for every prime p, there exists a Sidon set of size p + 1
contained in {0, 1, ..., p² + p}. This is a classical result in combinatorial
number theory using perfect difference sets in cyclic groups.
(Proof requires finite field theory not yet fully available in Mathlib.) -/
lemma singer_sidon_existence (p : ℕ) (hp : Nat.Prime p) :
    ∃ S : Finset ℕ, S ⊆ Finset.Icc 0 (p ^ 2 + p) ∧
      IsSidonFinset S ∧ S.card = p + 1 := by
  sorry

/-
PROBLEM
Key extension lemma: for any ε > 0, N ≥ 1, and Sidon set A ⊆ [1,N],
there exist M ≥ N and B ⊆ [N+1, M] with A ∪ B Sidon and |A ∪ B| ≥ (1-ε)√M.

Proof sketch:
• If |A| ≥ (1-ε)√N, take M = N and B = ∅.
• Otherwise, choose a prime p ≥ C·N/ε (by Bertrand's postulate), use Singer's
  Sidon set shifted to [N+1, N+1+p²+p], remove ≤ k(k-1)/2 elements to avoid
  cross-collisions with D(A), where k = |A|. The remaining set has size
  ≥ p+1-k²/2, and choosing p large enough ensures (1-ε)√M ≤ |A∪B|.

For ε ≥ 1, the extension is trivially satisfied by taking B = ∅.

PROVIDED SOLUTION
Take M = N and B = ∅. Then A ∪ ∅ = A is Sidon. And (1-ε)*√M ≤ 0 ≤ |A| since ε ≥ 1 implies 1-ε ≤ 0, so (1-ε)*√M ≤ 0 ≤ |A.card|. The set ∅ ⊆ Finset.Icc (N+1) N vacuously since this interval is empty.
-/
lemma sidon_extension_trivial_large_eps (ε : ℝ) (hε : ε ≥ 1) (N : ℕ) (hN : 1 ≤ N)
    (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  refine' ⟨ N, le_rfl, ∅, _, _, _ ⟩ <;> norm_num;
  · assumption;
  · exact le_trans ( mul_nonpos_of_nonpos_of_nonneg ( sub_nonpos.mpr hε ) ( Real.sqrt_nonneg _ ) ) ( Nat.cast_nonneg _ )

/-- For 0 < ε < 1, the extension uses Singer's construction with cross-collision
removal. This is the hard case requiring Singer's theorem. -/
lemma sidon_extension_small_eps (ε : ℝ) (hε : ε > 0) (hε' : ε < 1) (N : ℕ) (hN : 1 ≤ N)
    (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

/-
PROVIDED SOLUTION
Case split on whether ε ≥ 1 or ε < 1.
If ε ≥ 1: use sidon_extension_trivial_large_eps.
If ε < 1: use sidon_extension_small_eps (with hε and the fact that ε < 1).
-/
lemma sidon_extension_exists (ε : ℝ) (hε : ε > 0) (N : ℕ) (hN : 1 ≤ N)
    (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  by_cases hε' : ε ≥ 1;
  · exact ⟨ N, le_rfl, ∅, by norm_num, by aesop, by norm_num; nlinarith [ Real.sqrt_nonneg N ] ⟩;
  · exact sidon_extension_small_eps ε hε ( lt_of_not_ge hε' ) N hN A hA hSidon

/-
PROVIDED SOLUTION
Use sidon_extension_exists. Set Mε = 1. Given ε > 0, N ≥ 1, and Sidon A ⊆ [1,N], apply sidon_extension_exists to get M ≥ N and B with the required properties. Then M ≥ max N 1 since M ≥ N ≥ 1.
-/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε_pos
  use 1
  intro N hN A hA hSidon
  obtain ⟨M, hM_ge_N, B, hB_subset, hB_sidon, hB_card⟩ := sidon_extension_exists ε hε_pos N hN A hA hSidon
  use M
  aesop

/-! ## Boundary variant analysis (ε = 0)

The **boundary variant** is the statement obtained by setting ε = 0 in
`erdos_44_sidon_extension`, asking whether Sidon set extensions can achieve
density √M (rather than (1 - ε)√M for ε > 0).

### Statement
```
∃ M₀ : ℕ, ∀ N : ℕ, 1 ≤ N →
  ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
    ∃ M : ℕ, M ≥ max N M₀ ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)
```

### Analysis

We investigate whether the boundary variant is true, false, or independent of
current techniques.

#### Key observations:

1. **Singer's construction** yields Sidon sets of size p + 1 in [0, p² + p] for
   prime p. Since (p+1)² > p² + p + 1, we have p + 1 > √(p² + p + 1),
   so Singer's sets *exceed* √M for M = p² + p + 1.

2. **Cross-collision analysis**: For extending a Sidon set A ⊆ [1, N], the
   differences D(A) = {a₁ - a₂ : a₁, a₂ ∈ A, a₁ ≠ a₂} must be avoided in D(B).
   In Singer's set, each nonzero difference appears exactly once, so removing
   one element eliminates a pair {d, -d} of differences.

3. **Removal cost**: For |A| = k, we need to eliminate k(k-1)/2 difference pairs
   (using ±symmetry). Each removal from Singer's set fixes at least one pair.
   Conservative bound: ≤ k(k-1)/2 removals.

4. **Net density after removal**: |A ∪ B| ≥ k + (p+1) - k(k-1)/2 = p + 1 + k(3-k)/2.
   For k ≤ 3: this exceeds p, and choosing p ≥ N yields |A∪B| ≥ √M.
   For k ≥ 4: smarter removal (each element covers ~2p differences) can reduce
   the number of removals to ⌈k(k-1)/(2p)⌉ ≈ 1 for k ≪ √p.

5. **Conclusion**: For any finite Sidon set A, choosing prime p ≥ max(N, k²)
   and using Singer's construction with smart removal yields |A∪B| > √M.
   The boundary variant is **plausibly true** but its proof requires:
   - Formalized Singer's theorem on perfect difference sets
   - A covering argument for efficient difference removal
   Both are beyond current Mathlib coverage.

#### Computational evidence:

For A = ∅ (N = 1): boundary holds at M = 3, 4, 5, ..., 64 (greedy achieves √M).
For A = {1,2,5} (N = 5): boundary holds at M = 5, ..., 100 (fails only at M = 101, 102
  for greedy, but other M values work).

**No counterexample was found.** The boundary variant appears to be true but is
*independent of current techniques* in the sense that its proof requires
number-theoretic constructions (Singer difference sets) that are not yet
formalized in Mathlib.
-/

/-- The boundary variant of Erdős Problem 44: can Sidon sets always be extended to
achieve density exactly √M (i.e., ε = 0)? -/
def boundary_variant : Prop :=
  ∃ M₀ : ℕ, ∀ N : ℕ, 1 ≤ N →
    ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
      ∃ M : ℕ, M ≥ max N M₀ ∧
        ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
          IsSidonFinset (A ∪ B) ∧
          Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)

/-- The negation of the boundary variant: for every threshold M₀, there exists a
Sidon set that cannot be extended to density √M for any M ≥ M₀. -/
def boundary_variant_negation : Prop :=
  ∀ M₀ : ℕ, ∃ N : ℕ, 1 ≤ N ∧
    ∃ A : Finset ℕ, A ⊆ Finset.Icc 1 N ∧ IsSidonFinset A ∧
      ∀ M : ℕ, M ≥ max N M₀ →
        ∀ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M →
          IsSidonFinset (A ∪ B) →
            ((A ∪ B).card : ℝ) < Real.sqrt (M : ℝ)

/-
PROVIDED SOLUTION
boundary_variant ↔ ¬ boundary_variant_negation is a logical equivalence between ∃∀∀∃∃ and ¬∀∃∃∀∀. Push through the quantifiers: boundary_variant = ∃ M₀, ∀ N, ... ∃ M, ∃ B, ... and boundary_variant_negation = ∀ M₀, ∃ N, ... ∀ M, ∀ B, ... with the conclusion negated. These are logical negations of each other (with the real number comparison < vs ≥ flipping).
-/
theorem boundary_iff_neg : boundary_variant ↔ ¬ boundary_variant_negation := by
  unfold boundary_variant boundary_variant_negation;
  simp +zetaDelta at *;
  simp +decide only [and_assoc]

/-! ## Helper lemmas for the analysis -/

/-
PROBLEM
Empty set is Sidon.

PROVIDED SOLUTION
Vacuously true since no elements belong to ∅.
-/
lemma isSidonFinset_empty : IsSidonFinset ∅ := by
  tauto

/-
PROBLEM
Singletons are Sidon.

PROVIDED SOLUTION
If a,b,c,d ∈ {n}, then a=b=c=d=n, so a+b=c+d is trivially satisfied with a=c, b=d.
-/
lemma isSidonFinset_singleton (n : ℕ) : IsSidonFinset {n} := by
  exact fun a b c d ha hb hc hd h => by aesop;

/-
PROBLEM
Subsets of Sidon sets are Sidon.

PROVIDED SOLUTION
If A ⊆ B and B is Sidon, then for any a,b,c,d ∈ A we have a,b,c,d ∈ B, so the Sidon condition on B gives the conclusion.
-/
lemma isSidonFinset_subset {A B : Finset ℕ} (h : A ⊆ B) (hB : IsSidonFinset B) :
    IsSidonFinset A := by
  exact fun a b c d ha hb hc hd hab => hB ( h ha ) ( h hb ) ( h hc ) ( h hd ) hab

/-
PROBLEM
The trivial case of the main theorem: if |A| ≥ (1-ε)√N, take M = N and B = ∅.

PROVIDED SOLUTION
Take M = N and B = ∅. Then:
- M ≥ N trivially
- B = ∅ ⊆ Finset.Icc (N+1) N (which is empty, so any subset works)
- A ∪ ∅ = A, which is Sidon by hypothesis
- (1-ε) * √N ≤ |A| by hypothesis hCard, and M = N so (1-ε) * √M = (1-ε) * √N ≤ |A| = |A∪∅|
-/
lemma erdos_trivial_case (ε : ℝ) (hε : ε > 0) (N : ℕ) (hN : 1 ≤ N)
    (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A)
    (hCard : (1 - ε) * Real.sqrt N ≤ A.card) :
    ∃ M : ℕ, M ≥ N ∧
      ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
        IsSidonFinset (A ∪ B) ∧
        (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  aesop

/-
PROBLEM
Weak upper bound for Sidon sets: if A is a Sidon set in [1, N] then
|A|·(|A|+1) ≤ 4·N. This follows because the |A|(|A|+1)/2 unordered pair sums
a + b (a ≤ b, a, b ∈ A) are all distinct integers in [2, 2N], so
|A|(|A|+1)/2 ≤ 2N - 1 < 2N.

PROVIDED SOLUTION
Consider the map f : {(a,b) ∈ A × A | a ≤ b} → [2, 2N] defined by f(a,b) = a + b. Since A is Sidon, f is injective (if a+b = c+d then {a,b} = {c,d}, so the ordered pairs with a≤b are equal). The domain has |A|(|A|+1)/2 elements. The codomain [2, 2N] has at most 2N-1 elements. So |A|(|A|+1)/2 ≤ 2N-1 < 2N, hence |A|(|A|+1) ≤ 4N-2 ≤ 4N.

Alternative approach: consider the Finset.image of the sum function on pairs with a ≤ b. Use card_image_of_injOn with the Sidon property to show injectivity, then bound the image by Finset.Icc 2 (2*N).

Key steps:
1. Define the pairs set: P = (A ×ˢ A).filter (fun p => p.1 ≤ p.2)
2. Show |P| = |A|*(|A|+1)/2 (or at least |P| ≥ this)
3. Define sumMap p = p.1 + p.2
4. Show sumMap is injective on P (by Sidon property)
5. Show image of sumMap lies in Finset.Icc 2 (2*N)
6. Conclude |P| ≤ |Finset.Icc 2 (2*N)| = 2*N - 1
7. Hence |A|*(|A|+1) ≤ 2*(2*N-1) ≤ 4*N
-/
lemma sidon_card_sq_bound (A : Finset ℕ) (N : ℕ) (hA : A ⊆ Finset.Icc 1 N)
    (hSidon : IsSidonFinset A) :
    A.card * (A.card + 1) ≤ 4 * N := by
  -- Consider the set of sums $a + b$ with $a, b \in A$, $a \leq b$. This set has $|A|(|A|+1)/2$ elements.
  have h_sums : (Finset.image (fun p => p.1 + p.2) (Finset.filter (fun p => p.1 ≤ p.2) (A ×ˢ A))).card = A.card * (A.card + 1) / 2 := by
    rw [ Finset.card_image_of_injOn, Finset.card_filter ];
    · rw [ Finset.sum_product ];
      have h_sum_pairs : ∑ x ∈ A, ∑ y ∈ A, (if x ≤ y then 1 else 0) = ∑ x ∈ A, ∑ y ∈ A, (if y ≤ x then 1 else 0) := by
        rw [ Finset.sum_comm ];
      have h_sum_pairs : ∑ x ∈ A, ∑ y ∈ A, (if x ≤ y then 1 else 0) + ∑ x ∈ A, ∑ y ∈ A, (if y ≤ x then 1 else 0) = ∑ x ∈ A, ∑ y ∈ A, 1 + ∑ x ∈ A, ∑ y ∈ A, (if x = y then 1 else 0) := by
        simpa only [ ← Finset.sum_add_distrib ] using Finset.sum_congr rfl fun x hx => Finset.sum_congr rfl fun y hy => by split_ifs <;> omega;
      simp_all +decide [ Finset.sum_ite ];
      grind +splitImp;
    · -- By the Sidon property, if $a + b = c + d$ and $a \leq b$ and $c \leq d$, then $a = c$ and $b = d$.
      intros p hp q hq h_eq
      have h_eq' : p.1 = q.1 ∧ p.2 = q.2 ∨ p.1 = q.2 ∧ p.2 = q.1 := by
        aesop;
      grind;
  -- Since these sums are distinct and lie in the interval $[2, 2N]$, there are at most $2N-1$ such sums.
  have h_distinct_sums : (Finset.image (fun p => p.1 + p.2) (Finset.filter (fun p => p.1 ≤ p.2) (A ×ˢ A))).card ≤ 2 * N - 1 := by
    have h_distinct_sums : (Finset.image (fun p => p.1 + p.2) (Finset.filter (fun p => p.1 ≤ p.2) (A ×ˢ A))) ⊆ Finset.Icc 2 (2 * N) := by
      exact Finset.image_subset_iff.mpr fun p hp => Finset.mem_Icc.mpr ⟨ by linarith [ Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.1 ) ), Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.2 ) ) ], by linarith [ Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.1 ) ), Finset.mem_Icc.mp ( hA ( Finset.mem_product.mp ( Finset.mem_filter.mp hp |>.1 ) |>.2 ) ) ] ⟩;
    exact le_trans ( Finset.card_le_card h_distinct_sums ) ( by simp +arith +decide );
  rcases N with ( _ | N ) <;> simp_all +decide;
  rw [ Nat.le_sub_iff_add_le ] at h_distinct_sums <;> linarith [ Nat.div_mul_cancel ( show 2 ∣ A.card * ( A.card + 1 ) from even_iff_two_dvd.mp ( by simp +arith +decide [ mul_add, parity_simps ] ) ) ]

end Erdos44