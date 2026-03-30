/-
Experiment ID: 6ea335c4-6e56-4ecb-904e-2f40df223729
Move: counterexample_mode
Phase: consolidation
Modification: {"target": "most_fragile_variant"}
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
  sorry

/-!
## Fragile variant and its refutation

The **most fragile observed variant** of the Erdős–44 Sidon extension theorem is obtained
by promoting the existential quantifier `∃ M` to a universal quantifier `∀ M`. This
demands that for *every* sufficiently large `M`, one can extend `A` to a Sidon set of
density `(1 − ε)√M` inside `[1, M]`. The original statement only asks for *some* such `M`.

This universal variant is false. The counterexample is elementary:

* **ε = 1/2, A = {1}, N = M = max 5 Mε**.
* Since `N + 1 > M = N`, the interval `[N+1, M]` is empty, forcing `B = ∅`.
* Then `|A ∪ B| = |{1}| = 1`, but `(1 − 1/2) √M = √M / 2 ≥ √5 / 2 > 1`.
* Hence the density bound fails for *every* Sidon extension `B` at this `M`.

This witnesses that the `∃ M` quantifier is *essential* to the conjecture: the
extension may require choosing `M` much larger than `N` to accommodate a fresh
Sidon tail of the required density.
-/

/-- The fragile "∀ M" variant of Erdős problem 44: for every large M, one can extend any
Sidon subset of [1,N] to a Sidon subset of [1,M] with density ≥ (1−ε)√M.
This is the statement obtained by changing `∃ M` to `∀ M` in `erdos_44_sidon_extension`. -/
def erdos_44_fragile_variant : Prop :=
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∀ M : ℕ, M ≥ max N Mε →
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)

/-
PROBLEM
The singleton {1} is a Sidon set.

PROVIDED SOLUTION
Unfold IsSidonFinset. All four elements a,b,c,d must be in {1}, so a=b=c=d=1. Then a=c ∧ b=d is trivially true.
-/
lemma sidon_singleton_one : IsSidonFinset {1} := by
  -- In this case, the only elements in the set are 1, so the condition is trivially satisfied.
  intros a ha b hb c hc d hd habcd
  aesop

/-
PROBLEM
When M = N, the interval [N+1, M] is empty (as a Finset of ℕ).

PROVIDED SOLUTION
Finset.Icc (N+1) N = ∅ because N+1 > N. Use simp or Finset.Icc_eq_empty with omega.
-/
lemma Icc_succ_self_eq_empty (N : ℕ) : Finset.Icc (N + 1) N = ∅ := by
  aesop

/-
PROBLEM
√5 / 2 > 1.

PROVIDED SOLUTION
√5 > 2 because 5 > 4 = 2². So √5/2 > 1. Use Real.lt_sqrt or norm_num and nlinarith with Real.sq_sqrt.
-/
lemma sqrt_five_half_gt_one : (1 : ℝ) < Real.sqrt 5 / 2 := by
  nlinarith [ Real.sqrt_nonneg 5, Real.sq_sqrt ( show 0 ≤ 5 by norm_num ) ]

/-
PROBLEM
The fragile "∀ M" variant is **false**.

PROVIDED SOLUTION
Unfold erdos_44_fragile_variant. We must show that for some ε > 0, for all Mε : ℕ, there exist N ≥ 1, A, and M such that no B works.

Use ε = 1/2 (so 1 - ε = 1/2).
For any Mε : ℕ, choose N = max 5 Mε and A = {1} (which is Sidon by sidon_singleton_one, and ⊆ [1,N] since N ≥ 5 ≥ 1).
Choose M = N (so M ≥ max N Mε since N = max 5 Mε).

Then [N+1, M] = [N+1, N] = ∅ by Icc_succ_self_eq_empty. So any B ⊆ ∅ means B = ∅.
So A ∪ B = {1} ∪ ∅ = {1}, and |{1}| = 1.

The density bound requires (1/2) * √N ≤ 1, i.e., √N ≤ 2, i.e., N ≤ 4.
But N = max 5 Mε ≥ 5, so √N ≥ √5 and (1/2)√N ≥ √5/2 > 1 by sqrt_five_half_gt_one.
This gives a contradiction.

Key technical details:
- B ⊆ Finset.Icc (N+1) N = ∅ implies B = ∅ (use Finset.subset_empty.mp after rewriting with Icc_succ_self_eq_empty).
- {1} ∪ ∅ = {1} and Finset.card {1} = 1 (by simp).
- For the √ bound: √(↑N) ≥ √5 because N ≥ 5, and then use sqrt_five_half_gt_one.
- Use Real.sqrt_le_sqrt to get √5 ≤ √N from 5 ≤ N.
- The density bound ¬((1/2) * √N ≤ 1) follows from (1/2) * √N ≥ (1/2) * √5 > 1.
-/
theorem erdos_44_fragile_variant_false : ¬ erdos_44_fragile_variant := by
  unfold erdos_44_fragile_variant;
  push_neg;
  use 1 / 2;
  refine' ⟨ by norm_num, fun Mε => ⟨ 5 + Mε, by linarith, { 1 }, _, _, 5 + Mε, _, _ ⟩ ⟩ <;> norm_num;
  · grind;
  · exact sidon_singleton_one;
  · exact fun _ => by nlinarith [ Real.sqrt_nonneg ( 5 + Mε : ℝ ), Real.sq_sqrt ( show 0 ≤ 5 + ( Mε : ℝ ) by positivity ) ] ;

end Erdos44