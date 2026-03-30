/-
Experiment ID: c418e365-2654-4c30-87df-c0bfefebb532
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
## Fragile variant analysis

The **most fragile observed variant** of the Erdős 44 statement is obtained by
removing the extension mechanism — i.e., forcing `B = ∅` (equivalently `M = N`).
This variant would assert:

> ∀ ε > 0, ∀ large enough N, **every** Sidon set A ⊆ [1, N] satisfies
> |A| ≥ (1 − ε) √N.

This is false: the singleton `{1}` is a Sidon subset of `[1, N]` for every `N`,
but its cardinality is `1`, which is strictly less than `(1 − ε) √N` once `N` is
large enough.

The theorems below formalize:
1. `{1}` is Sidon (`singleton_one_sidon`).
2. The no-extension variant is false (`erdos_44_no_extension_false`), witnessed
   by `ε = 1/4` and the family `A = {1}`.
-/

/-- `{1}` is a Sidon set. -/
theorem singleton_one_sidon : IsSidonFinset {1} := by
  intros a b c d ha hb hc hd habcd
  aesop

/-- `{1}` is a subset of `Finset.Icc 1 N` whenever `1 ≤ N`. -/
theorem singleton_one_subset_Icc {N : ℕ} (hN : 1 ≤ N) :
    ({1} : Finset ℕ) ⊆ Finset.Icc 1 N := by
  grind

/-- For large enough `N`, `1 < (1 - 1/2) * √N`, so the singleton cannot satisfy
the no-extension density bound. -/
theorem density_bound_exceeds_one :
    ∃ N₀ : ℕ, ∀ N : ℕ, N₀ ≤ N →
      (1 : ℝ) < (1 - 1 / 2) * Real.sqrt (N : ℝ) := by
  exact ⟨16, fun N hN => by
    nlinarith [Real.sqrt_nonneg N, Real.sq_sqrt (Nat.cast_nonneg N),
               (by norm_cast : (16 : ℝ) ≤ N)]⟩

/-- The **no-extension variant** of Erdős 44 is **false**:

> ¬ ∀ ε > 0, ∃ N₀, ∀ N ≥ N₀, ∀ Sidon A ⊆ [1, N],  |A| ≥ (1 − ε) √N.

Witnessed by `ε = 1/4` and the family `A_N = {1}`. -/
theorem erdos_44_no_extension_false :
    ¬ (∀ ε : ℝ, ε > 0 →
      ∃ N₀ : ℕ, ∀ N : ℕ, N₀ ≤ N → 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          (1 - ε) * Real.sqrt (N : ℝ) ≤ (A.card : ℝ)) := by
  norm_num +zetaDelta at *
  use 1 / 4
  refine ⟨by norm_num, fun x => ⟨x + 9, by linarith, by linarith, {1}, ?_, ?_, ?_⟩⟩
    <;> norm_num [IsSidonFinset]
  · aesop
  · nlinarith [Real.sqrt_nonneg (x + 9 : ℝ),
               Real.sq_sqrt (by positivity : 0 ≤ (x : ℝ) + 9)]

end Erdos44
