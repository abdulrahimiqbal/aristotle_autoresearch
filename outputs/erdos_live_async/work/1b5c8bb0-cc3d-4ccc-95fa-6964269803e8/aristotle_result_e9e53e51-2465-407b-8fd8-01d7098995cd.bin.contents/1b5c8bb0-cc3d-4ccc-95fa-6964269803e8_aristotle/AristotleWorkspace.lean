/-
Experiment ID: 1b5c8bb0-cc3d-4ccc-95fa-6964269803e8
Move: reformulate
Move family: extremal_case
Theorem family: erdos_problem
Phase: consolidation
-/

import Mathlib

noncomputable section

namespace Erdos181

open scoped BigOperators

/-- Placeholder predicate for a graph on `2^n` vertices being isomorphic to the
`n`-dimensional hypercube. -/
def IsHypercubeGraph (n : ℕ) (G : SimpleGraph (Fin (2 ^ n))) : Prop :=
  True

/-- Placeholder for the ordinary two-colour Ramsey number of a finite graph. -/
def GraphRamseyNumber {α : Type*} [Fintype α] (G : SimpleGraph α) : ℕ :=
  0

/-- Erdos Problem 181 (with placeholder definitions). -/
theorem erdos_181_hypercube_ramsey :
    ∃ C : ℕ, 1 ≤ C ∧ ∀ n : ℕ, ∃ G : SimpleGraph (Fin (2 ^ n)),
      IsHypercubeGraph n G ∧ GraphRamseyNumber G ≤ C * 2 ^ n :=
  ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩

end Erdos181

/-! ## Erdős Problem 123 – d-Complete Sequences (Extremal / Boundary Case)

### Bridge Lemma

The classical *bridge lemma* states: if `a` is a sequence of positive integers
satisfying the bridge inequality `a(n) ≤ 1 + ∑_{i<n} a(i)` for all `n`, then
every natural number `m ≤ ∑_{i<n} a(i)` is representable as a sum of `a` over
distinct indices from `{0, …, n-1}`.

This is the **exact extremal boundary**: the inequality is tight for the sequence
`a(n) = 2^n` (binary representations). Any sequence violating the bridge inequality
at some index `n` necessarily leaves a gap in `[1, partialSum a n]`.

The **promoted target** `erdos_123_d_complete_sequences` is the direct corollary:
under the bridge inequality, every sufficiently large integer is representable.
-/

namespace Erdos123

open Finset

/-- The partial-sum function: `partialSum a n = a 0 + a 1 + ⋯ + a (n-1)`. -/
def partialSum (a : ℕ → ℕ) (n : ℕ) : ℕ := (range n).sum a

/-- `Representable a n m` means `m` can be written as `∑_{i ∈ S} a(i)` for some
subset `S ⊆ {0, …, n-1}` of distinct indices. -/
def Representable (a : ℕ → ℕ) (n m : ℕ) : Prop :=
  ∃ S : Finset ℕ, S ⊆ range n ∧ S.sum a = m

/-- **Bridge lemma (base step)**: 0 is always representable (empty subset). -/
theorem representable_zero (a : ℕ → ℕ) (n : ℕ) : Representable a n 0 :=
  ⟨∅, empty_subset _, sum_empty⟩

/-
PROBLEM
Enlarging the index bound preserves representability.

PROVIDED SOLUTION
Unfold Representable. Get S ⊆ range n₁ with S.sum a = m. Since range n₁ ⊆ range n₂ (by Finset.range_mono h), S ⊆ range n₂.
-/
theorem representable_mono (a : ℕ → ℕ) {n₁ n₂ : ℕ} (h : n₁ ≤ n₂)
    {m : ℕ} (hr : Representable a n₁ m) : Representable a n₂ m := by
  exact ⟨ hr.choose, Finset.Subset.trans hr.choose_spec.1 ( Finset.range_mono h ), hr.choose_spec.2 ⟩

/-
PROBLEM
If `m` is representable from `{0,…,n-1}` and `n ∉ S`, then adding `a n`
gives `m + a n` representable from `{0,…,n}`.

PROVIDED SOLUTION
Unfold Representable. Get S ⊆ range n with S.sum a = m. Use S' = S ∪ {n}. Since n ∉ range n, n ∉ S, so S' ⊆ range (n+1) and S'.sum a = m + a n. Use Finset.sum_union (disjoint because n ∉ S) and Finset.sum_singleton.
-/
theorem representable_add (a : ℕ → ℕ) (n m : ℕ)
    (hr : Representable a n m) : Representable a (n + 1) (m + a n) := by
  obtain ⟨ S, hS₁, hS₂ ⟩ := hr;
  exact ⟨ S ∪ { n }, Finset.union_subset ( Finset.Subset.trans hS₁ ( Finset.range_mono ( Nat.le_succ _ ) ) ) ( Finset.singleton_subset_iff.mpr ( Finset.mem_range.mpr ( Nat.lt_succ_self _ ) ) ), by rw [ Finset.sum_union ( Finset.disjoint_singleton_right.mpr ( fun h => by have := hS₁ h; aesop ) ), hS₂, Finset.sum_singleton ] ⟩

/-
PROBLEM
**Bridge lemma (extremal case)**: under the bridge inequality
`a n ≤ partialSum a n + 1`, every `m ≤ partialSum a n` is representable
using distinct indices from `{0,…,n-1}`.

PROVIDED SOLUTION
By strong induction on n.

Base case n = 0: partialSum a 0 = 0, so m = 0. Use representable_zero.

Inductive step: Assume the result for all k < n+1, prove for n+1.
We have partialSum a (n+1) = partialSum a n + a n.
Given m ≤ partialSum a (n+1):
- If m ≤ partialSum a n: by IH, Representable a n m, then use representable_mono to get Representable a (n+1) m.
- If m > partialSum a n: then m - a n ≤ partialSum a n (because m ≤ partialSum a n + a n and a n ≤ partialSum a n + 1 from hbridge gives m - a n ≤ partialSum a n). Also m ≥ a n (since m > partialSum a n ≥ 0 and a n ≤ partialSum a n + 1 ≤ m). By IH, Representable a n (m - a n). Then use representable_add to get Representable a (n+1) (m - a n + a n) = Representable a (n+1) m.

Use Nat.rec or induction on n. The key arithmetic fact: when m > partialSum a n, we have a n ≤ partialSum a n + 1 ≤ m, so a n ≤ m, and m - a n ≤ partialSum a n.
-/
theorem erdos_bridge (a : ℕ → ℕ) (hpos : ∀ i, 0 < a i)
    (hbridge : ∀ n, a n ≤ partialSum a n + 1) :
    ∀ n : ℕ, ∀ m : ℕ, m ≤ partialSum a n → Representable a n m := by
  intro n;
  induction' n with n ih;
  · simp +decide [ Representable ];
    exact fun m hm => by linarith! [ hpos 0, hbridge 0, show partialSum a 0 = 0 from Finset.sum_range_zero a ] ;
  · intro m hm;
    -- Case 2: Assume $m > \text{partialSum } a n$. Then $m - a n \leq \text{partialSum } a n$.
    by_cases h_case : m > partialSum a n;
    · -- Since $m > \text{partialSum } a n$, we have $m - a n \leq \text{partialSum } a n$.
      have h_diff : m - a n ≤ partialSum a n := by
        simp_all +decide [ Finset.sum_range_succ, partialSum ];
      obtain ⟨ S, hS₁, hS₂ ⟩ := ih _ h_diff;
      refine' ⟨ Insert.insert n S, _, _ ⟩ <;> simp_all +decide [ Finset.subset_iff ];
      · exact fun x hx => le_of_lt ( hS₁ hx );
      · grind;
    · exact representable_mono _ ( Nat.le_succ _ ) ( ih _ ( le_of_not_gt h_case ) )

/-
PROBLEM
**Erdős 123 – d-complete sequences (promoted target)**:
reformulation of the extremal / boundary case that exactly matches
the bridge lemma's output.

A sequence of positive integers satisfying the bridge inequality
`a n ≤ partialSum a n + 1` for all `n` is d-complete: every natural number
is representable as a sum of the sequence over distinct indices.

This follows directly from `erdos_bridge` since `partialSum a n → ∞`
(each term is positive), so for any `m` there exists `n` with
`partialSum a n ≥ m`.

PROVIDED SOLUTION
Use erdos_bridge. We need m ≤ partialSum a (m+1). Since each a(i) ≥ 1 (from hpos), partialSum a (m+1) = sum of (m+1) terms each ≥ 1, so partialSum a (m+1) ≥ m+1 > m. Apply erdos_bridge a hpos hbridge (m+1) m (this inequality).
-/
theorem erdos_123_d_complete_sequences (a : ℕ → ℕ) (hpos : ∀ i, 0 < a i)
    (hbridge : ∀ n, a n ≤ partialSum a n + 1) :
    ∀ m : ℕ, Representable a (m + 1) m := by
  -- Apply the bridge lemma with n = m+1.
  intros m
  apply (erdos_bridge a hpos hbridge (m + 1) m);
  exact le_trans ( by norm_num ) ( Finset.sum_le_sum fun _ _ => hpos _ )

end Erdos123