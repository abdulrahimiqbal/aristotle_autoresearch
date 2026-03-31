/-
Experiment ID: dd6f6d93-638e-42c2-9fa0-6db293ff1e3b
Move: counterexample_mode
Move family: adversarial_counterexample
Theorem family: erdos_problem
Phase: consolidation
Modification: {"mode": "adversarial", "target": "."}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- adversarial target: .
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
  intro a _ _ _ ha; exact absurd ha (by simp)

/-- Subsets of Sidon sets are Sidon. -/
lemma IsSidonFinset.subset {A B : Finset ℕ} (hA : IsSidonFinset A) (hBA : B ⊆ A) :
    IsSidonFinset B :=
  fun _ _ _ _ ha hb hc hd h => hA (hBA ha) (hBA hb) (hBA hc) (hBA hd) h

/-- Helper: when ε ≥ 1, the bound (1 - ε) * √M ≤ 0 ≤ |A ∪ B| is trivially satisfied
by taking B = ∅, since (1 - ε) ≤ 0 and √M ≥ 0. -/
lemma erdos_44_case_eps_ge_one :
    ∀ ε : ℝ, ε ≥ 1 →
      ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N 1 ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  -- Let's choose M = N and B = ∅.
  intro ε hε N hN A hA hSidon
  use N, by
    grind, ∅, by
    exact Finset.empty_subset _
  exact ⟨ by simpa using hSidon, by nlinarith [ Real.sqrt_nonneg N, show ( A ∪ ∅ |> Finset.card : ℝ ) ≥ 0 by positivity ] ⟩

/-!
## Analysis: Why the ε < 1 case is open

This theorem is a formalization of **Erdős Problem 44** on extending Sidon (B₂) sets
while maintaining near-optimal density. The case ε ≥ 1 is trivially proved above, but
the case 0 < ε < 1 remains an **open problem in additive combinatorics**.

### The core difficulty

For a Sidon set A ⊆ [1, N] and an extension B ⊆ [N+1, M], the union A ∪ B must satisfy:

1. **Internal Sidon property of B**: All pair sums within B are distinct.
2. **Cross-difference avoidance**: No nonzero difference of A equals a nonzero difference of B.
3. **Mixed-triple avoidance**: For all a ∈ A and b₁, b₂, b₃ ∈ B, a + b₁ ≠ b₂ + b₃.
4. **Reverse mixed-triple**: For all b ∈ B and a₁, a₂, a₃ ∈ A, b + a₁ ≠ a₂ + a₃.

### Dilation approach and its limitations

The cleanest construction uses dilation: B = {C + s·D : s ∈ S} where S is a known Sidon set,
C = 2(N+1), and D = N+1. This satisfies all four conditions above because:
- All differences of B are multiples of D = N+1 > N-1 ≥ max|diff(A)|
- min(B) = C = 2(N+1) > 2N-1 = max(a₂+a₃-a₁)
- b₂+b₃-b₁ = (m+2)(N+1) ∉ [1,N] for any integer m

However, this construction achieves density |B|/√M ≈ 1/√(N+1), which fails to reach
(1-ε)√M for large N when ε < 1 - 1/√(2(N+1)).

### What would be needed

A complete proof requires constructing Sidon sets with density approaching √M while
maintaining compatibility with an arbitrary given Sidon set A. This is equivalent to
solving the original Erdős problem, which remains open as of 2024.

Known constructions (Singer perfect difference sets, Erdős-Turán) achieve optimal
density √M for Sidon sets in [1,M], but ensuring compatibility with A ⊆ [1,N]
introduces constraints that no known technique can handle for all ε > 0 simultaneously.
-/

/-- A workspace-local Lean 4 stub for Erdos Problem 44. The formal-conjectures repo
contains a current version of this problem; this variant avoids repository-specific
imports while preserving the same mathematical shape.

**Status**: This is an open problem. The case ε ≥ 1 is proved via `erdos_44_case_eps_ge_one`.
The case 0 < ε < 1 requires constructing dense Sidon set extensions compatible with
arbitrary Sidon sets, which is the core content of Erdős Problem 44. -/
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
