/-
Counterexample for the "most fragile observed variant" of the Erdős 44 formalization.

The original `erdos_44_sidon_extension` allows extending a Sidon set A ⊆ [1,N] to a
larger Sidon set A ∪ B ⊆ [1,M] for some M ≥ N. The **most fragile variant** removes
this extension mechanism and asks whether every Sidon set A ⊆ [1,N] already satisfies
the density bound |(A| ≥ (1 − ε)√N.

This is false: the singleton {1} is a Sidon set in [1, N] for any N ≥ 1, but
|{1}| = 1 < (1 − ε)√N for any fixed ε ∈ (0,1) and sufficiently large N. Below we
formalize this counterexample.

This identifies the extension mechanism (∃ M, ∃ B) as the essential non-trivial
structural ingredient of the conjecture — without it, the statement collapses.
-/

import Mathlib

noncomputable section

namespace Erdos44Counterexample

open scoped BigOperators

/-- Sidon condition (copied from Main.lean for self-containment). -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-- The "no-extension" (most fragile) variant: asks whether every Sidon set in [1,N]
already meets the density bound, without any room to extend. -/
def fragile_variant : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ N₀ : ℕ, ∀ N : ℕ, N₀ ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        (1 - ε) * Real.sqrt (N : ℝ) ≤ ((A.card : ℕ) : ℝ)

/-
PROBLEM
The singleton {1} is always a Sidon set.

PROVIDED SOLUTION
All elements are 1, so a=b=c=d=1, and (a=c ∧ b=d) holds trivially.
-/
lemma singleton_sidon : IsSidonFinset {1} := by
  -- In this case, the set $A = \{1\}$ trivially satisfies the Sidon condition.
  simp [IsSidonFinset] at *;
  aesop

/-
PROBLEM
{1} ⊆ [1, N] for any N ≥ 1.

PROVIDED SOLUTION
1 ∈ Finset.Icc 1 N when 1 ≤ N, use Finset.singleton_subset_iff and Finset.mem_Icc.
-/
lemma singleton_subset_Icc {N : ℕ} (hN : 1 ≤ N) : ({1} : Finset ℕ) ⊆ Finset.Icc 1 N := by
  aesop

/-
PROBLEM
Key numerical fact: for ε = 1/2 and N = 100, we have
    (1 - 1/2) * √100 = 5 > 1 = |{1}|, so the bound fails.

PROVIDED SOLUTION
(1 - 1/2) * √100 = 1/2 * 10 = 5. The card of {1} is 1. So we need ¬(5 ≤ 1). Use norm_num and Real.sqrt_eq_... to evaluate √100 = 10 (since Real.sqrt 100 = 10 because 10^2 = 100). Then the inequality becomes 5 ≤ 1 which is false.
-/
lemma bound_violated : ¬ ((1 - (1 : ℝ) / 2) * Real.sqrt 100 ≤ (({1} : Finset ℕ).card : ℝ)) := by
  norm_num

/-
PROBLEM
The fragile variant (without extension) is **false**.

**Counterexample witness:** ε = 1/2, A = {1}, N = 100.
Then A is Sidon, A ⊆ [1, 100], but |A| = 1 < 5 = (1 − 1/2)·√100.

This shows that the extension mechanism `∃ M ≥ N, ∃ B ⊆ [N+1, M]` in the original
conjecture is essential — it is precisely what makes the statement non-trivially
plausible.

PROVIDED SOLUTION
Unfold fragile_variant. Introduce the hypothesis h. Specialize h with ε = 1/2 (which is > 0) to get N₀. Now take N = max N₀ 100 (or just N₀ + 100 or similar to ensure N₀ ≤ N and N ≥ 100). Use A = {1}, which is Sidon (singleton_sidon) and contained in [1,N] (singleton_subset_Icc). We get (1 - 1/2) * √N ≤ 1. But (1/2) * √N ≥ (1/2) * √100 = 5 > 1 for N ≥ 100. This contradicts the bound. Key steps: use singleton_sidon, singleton_subset_Icc, and bound_violated or a direct numerical argument that (1/2)*√N > 1 for N ≥ 100. Actually a cleaner approach: specialize with N = max N₀ 100. Then 1/2 * √N ≥ 1/2 * √100 = 5 > 1.
-/
theorem fragile_variant_is_false : ¬ fragile_variant := by
  -- Let's unfold the definition of `fragile_variant`.
  unfold fragile_variant;
  push_neg;
  use 1 / 4;
  norm_num +zetaDelta at *;
  intro N₀
  use 100 * (N₀ + 1)^2 + 100
  use by
    nlinarith
  use {1}
  simp [singleton_sidon];
  nlinarith [ Real.sqrt_nonneg ( 100 * ( N₀ + 1 ) ^ 2 + 100 ), Real.mul_self_sqrt ( by positivity : ( 0 : ℝ ) ≤ 100 * ( N₀ + 1 ) ^ 2 + 100 ) ]

end Erdos44Counterexample