/-
Experiment ID: 4a5341f3-55a3-4dd4-9a22-88b11597448f
Move: reformulate
Phase: consolidation
Modification: {"form": "every finite Sidon set can be completed to a near-extremal Sidon set after enlarging the ambient interval"}
-/

-- reformulation: every finite Sidon set can be completed to a near-extremal Sidon set after enlarging the ambient interval
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

/--
**Erdős Problem 44 – completion reformulation.**

Every finite Sidon set can be completed to a near-extremal Sidon set after
enlarging the ambient interval.

Concretely: for every `ε > 0` there is a threshold `Mε` such that, for every
`N ≥ 1` and every Sidon set `A ⊆ [1, N]`, one can find an `M ≥ max(N, Mε)` and
a set `B ⊆ [N+1, M]` so that

  • `A ∪ B` is still Sidon, and
  • `|A ∪ B| ≥ (1 − ε) √M`,

i.e. the completed set is within a `(1 − ε)` factor of the conjectured extremal
Sidon-set size `√M` in `[1, M]`.
-/
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry

end Erdos44
