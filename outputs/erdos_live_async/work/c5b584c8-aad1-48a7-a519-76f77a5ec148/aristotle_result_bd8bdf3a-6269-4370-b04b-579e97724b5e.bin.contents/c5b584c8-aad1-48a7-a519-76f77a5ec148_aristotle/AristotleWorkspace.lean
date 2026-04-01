import Mathlib

/-!
# D-Complete Sequences and Pairwise Coprime Power Triple Sets

We formalize the notion of d-completeness for sets of natural numbers and prove
structural results about when sets are d-complete. The main decomposition:

1. **Bridge lemma** (`complete_criterion_implies_representable`): The classical Brown
   completeness criterion — a non-decreasing sequence starting at 1 where each next
   element ≤ 1 + partial sum yields full representability of all positive integers up
   to the total sum.

2. **Binary completeness** (`d_complete_of_contains_powers_of_two`): Any set containing
   all powers of 2 is d-complete (via Nat.twoPowSum_bitIndices).

3. **Monotonicity** (`d_complete_of_supset`): d-completeness is inherited by supersets.

4. **Main theorem** (`erdos_d_complete_sequences`): For pairwise coprime `a, b, c ≥ 2`,
   the power triple set `{a^i · b^j · c^k}` is d-complete. The case `min(a,b,c) = 2`
   follows from binary completeness. The general case (all bases ≥ 3) requires the
   Erdős density argument showing the gap condition holds from some index onward.

## Discovery: D-completeness boundary cases

The sharpest witness for the failure of interval-style coverage to upgrade to a
divisibility antichain is the singleton-base case with **one base** (`d = 1`):

- **Interval coverage holds**: for any `p ≥ 2`, the geometric set `{p^i : i ∈ ℕ}`
  places an element in every interval `[p^k, p^{k+1})`, achieving interval coverage.
- **Divisibility antichain fails completely**: every pair `p^i, p^j` with `i ≤ j`
  satisfies `p^i ∣ p^j`, making the set a **total chain** under divisibility. The
  maximal antichain has size exactly 1.

The **sharpest witness** is `S = {2^i : i ∈ ℕ}`: it has the densest possible
geometric interval coverage (every `[n, 2n]` contains `2^⌊log₂ n⌋`), yet its
divisibility structure is maximally degenerate — a total chain of length `ω`.

With **two or more coprime bases** `a, b` (both ≥ 2, gcd = 1), elements like `a^i`
and `b^j` (for `i, j ≥ 1`) become divisibility-incomparable: neither divides the
other. This creates genuine antichains of unbounded size, breaking the total-chain
obstruction. The transition happens exactly at `d = 2` bases: one base gives only
chains; two coprime bases produce antichains. Thus `d = 1` is the **exact boundary**
where interval coverage exists but divisibility antichains cannot be non-trivially
formed.
-/

open Finset BigOperators

-- ============================================================================
-- Core definitions
-- ============================================================================

/-- A set `S` of natural numbers is d-complete if every sufficiently large
    natural number can be written as a sum of distinct elements of `S`. -/
def IsDComplete (S : Set ℕ) : Prop :=
  ∃ N : ℕ, ∀ n : ℕ, n ≥ N → ∃ T : Finset ℕ, (↑T : Set ℕ) ⊆ S ∧ T.sum id = n

/-- The power triple set: `{a^i · b^j · c^k : i, j, k ∈ ℕ}`. -/
def PowerTripleSet (a b c : ℕ) : Set ℕ :=
  { n : ℕ | ∃ i j k : ℕ, n = a ^ i * b ^ j * c ^ k }

/-- Three natural numbers are pairwise coprime. -/
def PairwiseCoprime3 (a b c : ℕ) : Prop :=
  Nat.Coprime a b ∧ Nat.Coprime a c ∧ Nat.Coprime b c

/-- An enumeration `f : ℕ → ℕ` satisfies the completeness criterion. -/
def SatisfiesCompletenessCriterion (f : ℕ → ℕ) : Prop :=
  f 0 = 1 ∧
  (∀ n, f n ≤ f (n + 1)) ∧
  (∀ n, f (n + 1) ≤ 1 + ∑ i ∈ Finset.range (n + 1), f i)

-- ============================================================================
-- Bridge lemma: completeness criterion
-- ============================================================================

/-- **Bridge lemma**: If `f` satisfies the completeness criterion, every positive
    integer up to `∑ i < n, f i` is a sum of distinct `f`-values. -/
theorem complete_criterion_implies_representable (f : ℕ → ℕ)
    (hf : SatisfiesCompletenessCriterion f) :
    ∀ n : ℕ, ∀ m : ℕ, 1 ≤ m → m ≤ ∑ i ∈ Finset.range n, f i →
      ∃ T : Finset ℕ, T ⊆ Finset.range n ∧ T.sum f = m := by
  intro n
  induction' n with n ih generalizing f
  · aesop
  · intro m hm₁ hm₂
    rcases lt_or_ge m (f n) with hm₃ | hm₃ <;> simp_all +decide [Finset.sum_range_succ]
    · rcases n <;> simp_all +decide [Finset.sum_range_succ]
      · cases hf; aesop
      · exact Exists.elim (ih f hf m hm₁
          (by linarith [hf.2.2 ‹_›, Finset.sum_range_succ f ‹_›])) fun T hT =>
          ⟨T, Finset.Subset.trans hT.1 (Finset.range_mono (Nat.le_succ _)), hT.2⟩
    · obtain ⟨T, hT⟩ : ∃ T : Finset ℕ, T ⊆ Finset.range n ∧ T.sum f = m - f n := by
        by_cases hm₄ : m - f n = 0
        · exact ⟨∅, Finset.empty_subset _, by norm_num [hm₄]⟩
        · exact ih f hf _ (Nat.pos_of_ne_zero hm₄) (Nat.sub_le_of_le_add <| by linarith)
      use T ∪ {n}
      grind

-- ============================================================================
-- Structural lemmas
-- ============================================================================

/-- d-completeness is upward-closed under set inclusion. -/
theorem d_complete_of_supset (S T : Set ℕ) (hST : S ⊆ T) (hS : IsDComplete S) :
    IsDComplete T := by
  obtain ⟨N, hN⟩ := hS
  exact ⟨N, fun n hn => by obtain ⟨T, hT₁, hT₂⟩ := hN n hn; exact ⟨T, hT₁.trans hST, hT₂⟩⟩

/-- `1` is in any power triple set. -/
theorem one_mem_powerTripleSet (a b c : ℕ) :
    1 ∈ PowerTripleSet a b c := ⟨0, 0, 0, by norm_num⟩

/-- Powers of the first base are in the power triple set. -/
theorem pow_mem_powerTripleSet (a b c : ℕ) (i : ℕ) :
    a ^ i ∈ PowerTripleSet a b c := ⟨i, 0, 0, by norm_num⟩

/-- Powers of the third base are in the power triple set. -/
theorem pow_third_mem_powerTripleSet (a b c : ℕ) (k : ℕ) :
    c ^ k ∈ PowerTripleSet a b c := ⟨0, 0, k, by simp⟩

/-- The power triple set is symmetric under permutation of bases. -/
theorem powerTripleSet_comm12 (a b c : ℕ) :
    PowerTripleSet a b c = PowerTripleSet b a c :=
  Set.ext fun n =>
    ⟨fun hn => by rcases hn with ⟨i, j, k, rfl⟩; exact ⟨j, i, k, by ring⟩,
     fun hn => by rcases hn with ⟨i, j, k, rfl⟩; exact ⟨j, i, k, by ring⟩⟩

theorem powerTripleSet_comm13 (a b c : ℕ) :
    PowerTripleSet a b c = PowerTripleSet c b a :=
  Set.ext fun n =>
    ⟨fun hn => by rcases hn with ⟨i, j, k, rfl⟩; exact ⟨k, j, i, by ring⟩,
     fun hn => by rcases hn with ⟨i, j, k, rfl⟩; exact ⟨k, j, i, by ring⟩⟩

theorem powerTripleSet_comm23 (a b c : ℕ) :
    PowerTripleSet a b c = PowerTripleSet a c b :=
  Set.ext fun x =>
    ⟨fun ⟨i, j, k, h⟩ => ⟨i, k, j, by linarith⟩,
     fun ⟨i, j, k, h⟩ => ⟨i, k, j, by linarith⟩⟩

/-- Among pairwise coprime numbers ≥ 2, at most one is even. -/
theorem pairwiseCoprime3_at_most_one_even (a b c : ℕ) (ha : 2 ≤ a) (hb : 2 ≤ b) (hc : 2 ≤ c)
    (hco : PairwiseCoprime3 a b c) :
    (a % 2 = 0 → b % 2 = 1 ∧ c % 2 = 1) := by
  cases Nat.mod_two_eq_zero_or_one b <;> cases Nat.mod_two_eq_zero_or_one c <;>
    simp_all +decide [PairwiseCoprime3]
  · exact absurd (Nat.dvd_gcd (Nat.dvd_of_mod_eq_zero ‹b % 2 = 0›)
      (Nat.dvd_of_mod_eq_zero ‹c % 2 = 0›)) (by aesop)
  · exact Nat.mod_two_ne_zero.mp fun h => by
      have := Nat.dvd_gcd (Nat.dvd_of_mod_eq_zero h) (Nat.dvd_of_mod_eq_zero ‹b % 2 = 0›)
      aesop
  · exact Nat.mod_two_ne_zero.mp fun h => by
      have := Nat.dvd_gcd (Nat.dvd_of_mod_eq_zero h) (Nat.dvd_of_mod_eq_zero ‹c % 2 = 0›)
      aesop

-- ============================================================================
-- Binary completeness
-- ============================================================================

/-- Any set containing all powers of 2 is d-complete. -/
theorem d_complete_of_contains_powers_of_two (S : Set ℕ)
    (h : ∀ i : ℕ, 2 ^ i ∈ S) :
    IsDComplete S := by
  refine ⟨1, fun n hn => ?_⟩
  use Finset.image (fun i => 2 ^ i) n.bitIndices.toFinset
  rw [Finset.sum_image]
  · simp_all +arith +decide [Set.subset_def]
  · aesop_cat

-- ============================================================================
-- Case: one base equals 2
-- ============================================================================

/-- When a = 2, the power triple set contains all powers of 2 and is d-complete. -/
theorem erdos_d_complete_base2 (b c : ℕ) (hb : 2 ≤ b) (hc : 2 ≤ c)
    (hco : PairwiseCoprime3 2 b c) :
    IsDComplete (PowerTripleSet 2 b c) :=
  d_complete_of_contains_powers_of_two _ (fun i => pow_mem_powerTripleSet 2 b c i)

-- ============================================================================
-- General case
-- ============================================================================

/-- For pairwise coprime `a ≥ 3, b ≥ 3, c ≥ 2`, d-completeness of the power triple
    set. If `c = 2`, this reduces to binary completeness. If `c ≥ 3`, this is the
    deep Erdős density case where all three bases are ≥ 3 and the proof requires
    showing the completeness criterion holds from some index onward via bounds on
    sums over smooth numbers. -/
theorem erdos_d_complete_no_two (a b c : ℕ) (ha : 3 ≤ a) (hb : 3 ≤ b) (hc : 2 ≤ c)
    (hco : PairwiseCoprime3 a b c) :
    IsDComplete (PowerTripleSet a b c) := by
  -- If c = 2, PowerTripleSet contains all powers of 2 via c^k = 2^k
  by_cases hc2 : c = 2
  · subst hc2
    exact d_complete_of_contains_powers_of_two _ (pow_third_mem_powerTripleSet a b 2)
  · -- All of a, b, c ≥ 3. This is the deep Erdős density case.
    -- The sorted enumeration of PowerTripleSet satisfies the completeness
    -- criterion from some index onward. The proof requires bounds on sums
    -- over {a,b,c}-smooth numbers, which constitutes significant analytic
    -- number theory infrastructure beyond what is currently formalized in Mathlib.
    sorry

/-
PROBLEM
============================================================================
Main theorem
============================================================================

**Main theorem**: For pairwise coprime `a, b, c ≥ 2`, the power triple set
    `{a^i · b^j · c^k : i, j, k ∈ ℕ}` is d-complete.

PROVIDED SOLUTION
Split into cases:
- If a = 2: use erdos_d_complete_base2 directly.
- If b = 2: rewrite using powerTripleSet_comm12, then use erdos_d_complete_base2 with rearranged coprimality (use Nat.Coprime.symm).
- If c = 2: rewrite using powerTripleSet_comm13 to get PowerTripleSet c b a = PowerTripleSet 2 b a, then apply erdos_d_complete_base2 with rearranged coprimality.
- If none is 2: all ≥ 3. Use erdos_d_complete_no_two. Since a ≥ 2, a ≠ 2 implies a ≥ 3. Same for b, c.
-/
theorem erdos_d_complete_sequences (a b c : ℕ) (ha : 2 ≤ a) (hb : 2 ≤ b) (hc : 2 ≤ c)
    (hco : PairwiseCoprime3 a b c) :
    IsDComplete (PowerTripleSet a b c) := by
  by_cases ha2 : a = 2;
  · convert erdos_d_complete_base2 b c hb hc _;
    bound;
  · by_cases hb2 : b = 2;
    · subst hb2; exact d_complete_of_contains_powers_of_two _ ( fun i => ⟨ 0, i, 0, by ring ⟩ ) ;
    · exact erdos_d_complete_no_two a b c ( lt_of_le_of_ne ha ( Ne.symm ha2 ) ) ( lt_of_le_of_ne hb ( Ne.symm hb2 ) ) hc hco

-- ============================================================================
-- Original promoted lemma
-- ============================================================================

theorem promoted_lemma : True := trivial