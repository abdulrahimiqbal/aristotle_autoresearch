/-
Experiment ID: 9a354742-ab8b-47ee-b156-eab9d939a3a1
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

/-! ## Fragility Analysis

We identify three structural witnesses exposing the fragility of `erdos_44_sidon_extension`.

### Witness 1: The `Mε` quantifier is vacuous

The existential `∃ Mε` in the statement is superfluous: since `M` is existentially
quantified with `M ≥ max N Mε`, setting `Mε = 0` reduces the constraint to `M ≥ N`,
which any valid extension must satisfy anyway. The original statement is logically
equivalent to the simpler form without `Mε`. This makes the apparent "uniformity"
parameter an illusion — the statement carries no more content than the `Mε`-free version.
-/

/-
PROBLEM
The original statement implies the simplified version without Mε: just drop Mε
    and weaken `M ≥ max N Mε` to `M ≥ N`.

PROVIDED SOLUTION
Given h, for any ε > 0, get Mε from h. For any N, A, use h to get M ≥ max N Mε. Since M ≥ max N Mε ≥ N, we have M ≥ N. Return M and the rest of the conclusion.
-/
theorem erdos_44_implies_no_Mε
    (h : ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) :
    ∀ ε : ℝ, ε > 0 →
      ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ N ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  exact fun ε hε N hN A hA hA' => by obtain ⟨ Mε, hMε ⟩ := h ε hε; obtain ⟨ M, hM₁, B, hB₁, hB₂, hB₃ ⟩ := hMε N hN A hA hA'; exact ⟨ M, le_trans ( le_max_left _ _ ) hM₁, B, hB₁, hB₂, hB₃ ⟩ ;

/-
PROBLEM
The simplified version without Mε implies the original: witness `Mε = 0`.

PROVIDED SOLUTION
Given h, for any ε > 0, use Mε = 0. For any N ≥ 1, A, apply h to get M ≥ N. Then M ≥ max N 0 since max N 0 = N (as N ≥ 1 ≥ 0). Return M and the rest.
-/
theorem no_Mε_implies_erdos_44
    (h : ∀ ε : ℝ, ε > 0 →
      ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ N ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  intro ε hε; use 0; aesop;

/-! ### Witness 2: The "bounded extension" variant is false

The most fragile observed variant is obtained by collapsing the existential `∃ M` — i.e.,
requiring the extension to work within `[1, N]` itself (setting `M = N`, so `B = ∅`).
This variant asserts that **every** Sidon set in `[1, N]` already has near-`√N` elements,
which is trivially false: the singleton `{1}` is Sidon in `[1, N]` for any `N`, but has
only 1 element — far below `(1 - ε) √N` for large `N`. This is the concrete falsifying
witness for the most fragile variant.
-/

/-
PROBLEM
{1} is a Sidon set.

PROVIDED SOLUTION
Unfold IsSidonFinset. For a, b, c, d ∈ {1}, all are equal to 1. So a = c and b = d. Left disjunct.
-/
theorem sidon_singleton : IsSidonFinset {1} := by
  intro a b c d ha hb hc hd h_eq; aesop;

/-
PROBLEM
The bounded variant (M = N, no extension room) is false: the singleton {1}
    is a Sidon set in [1, N] but has only 1 element, far below (1-ε)√N for large N.

    Concretely, we use ε = 1/2 and N = 100: the singleton {1} ⊆ [1,100] is Sidon
    with |{1}| = 1, but (1 - 1/2) · √100 = 5 > 1.

PROVIDED SOLUTION
Push the negation. We need ε > 0, N ≥ 1, and a Sidon set A ⊆ [1,N] with |A| < (1-ε)√N. Use ε = 1/2, N = 100, A = {1}. Then {1} ⊆ Finset.Icc 1 100, {1} is Sidon (by sidon_singleton), |{1}| = 1, and (1 - 1/2) * √100 = (1/2) * 10 = 5 > 1. So the bound fails. The key numeric facts: (1:ℝ) < (1 - 1/2) * Real.sqrt 100, which is 1 < 5. Use Real.sqrt_eq_... or norm_num for √100 = 10.
-/
theorem bounded_variant_false :
    ¬ (∀ ε : ℝ, ε > 0 →
        ∀ N : ℕ, 1 ≤ N →
          ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
            (1 - ε) * Real.sqrt (N : ℝ) ≤ (A.card : ℝ)) := by
  simp +zetaDelta at *;
  refine' ⟨ 1 / 4, _, 81, _, _ ⟩ <;> norm_num;
  exact ⟨ ∅, by norm_num, by unfold IsSidonFinset; aesop, by norm_num ⟩

/-! ### Witness 3: Local extension obstruction

We exhibit a concrete Sidon set `{1, 2, 4}` and show that adding element `5`
breaks the Sidon property, since `1 + 5 = 6 = 2 + 4`. This is a local witness
that not every adjacent integer can be incorporated into an extension — the
extension step must carefully avoid sum collisions, illustrating the combinatorial
difficulty underlying the conjecture.
-/

/-
PROBLEM
{1, 2, 4} is a Sidon set.

PROVIDED SOLUTION
Unfold IsSidonFinset. For a, b, c, d ∈ {1, 2, 4} with a + b = c + d, enumerate all cases by membership (each is 1, 2, or 4) and check that the Sidon condition holds. Use decide or omega after case splitting on membership.
-/
theorem sidon_124 : IsSidonFinset ({1, 2, 4} : Finset ℕ) := by
  intro a b c d ha hb hc hd habcd; fin_cases ha <;> fin_cases hb <;> fin_cases hc <;> fin_cases hd <;> trivial;

/-
PROBLEM
Adding 5 to {1, 2, 4} breaks the Sidon property: 1 + 5 = 2 + 4 = 6,
    with 1 ≠ 2 and 1 ≠ 4, violating the Sidon condition.

PROVIDED SOLUTION
Unfold IsSidonFinset and push negation. We need to find a, b, c, d ∈ {1, 2, 4, 5} with a + b = c + d but neither (a = c ∧ b = d) nor (a = d ∧ b = c). Use a = 1, b = 5, c = 2, d = 4. Then 1 + 5 = 6 = 2 + 4, but 1 ≠ 2, 1 ≠ 4, so neither disjunct holds.
-/
theorem not_sidon_1245 : ¬ IsSidonFinset ({1, 2, 4, 5} : Finset ℕ) := by
  unfold IsSidonFinset; norm_num;

end Erdos44