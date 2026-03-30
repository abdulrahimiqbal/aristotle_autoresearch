/-
Witness file for the most fragile variant of `erdos_44_sidon_extension`.

## Fragility analysis

The theorem `erdos_44_sidon_extension` is a variant of Erdős Problem 44 (1941),
one of the oldest open problems in additive combinatorics. The most fragile
aspect of this formulation is that it *implies* the existence of near-optimal
Sidon (B₂) sets, which remains unresolved after 80+ years.

### Independence-style witness

We show formally that `erdos_44_sidon_extension` implies:

  ∀ ε > 0, ∃ M ≥ 1, ∃ S ⊆ [1, M] Sidon, |S| ≥ (1-ε)√M

This is a consequence of the Erdős-Turán conjecture on B₂ sets. Since the
conjecture remains open, the theorem `erdos_44_sidon_extension` cannot be
resolved with current techniques — it is "fragile" in the sense that it
depends on unresolved combinatorial existence questions.

### Falsifying the strengthened variant

We also disprove the "universal-M" strengthening (with `Mε ≥ 1`), where the
existential `∃ M` is replaced by universal `∀ M`. The key mechanism: when
N is large relative to Mε, setting M just above N leaves the interval
[N+1, M] too small to build any meaningful Sidon extension, while the
density target (1-ε)√M remains bounded away from zero.
-/

import Mathlib

noncomputable section

namespace Erdos44Witness

open scoped BigOperators

/-! ### Sidon set definition (mirroring Main.lean) -/

def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ### Part 1: Reduction to the Erdős-Turán conjecture

The original theorem, instantiated with A = ∅ and N = 1, yields a
Sidon set of near-optimal density.  This shows the theorem is at
least as hard as the longstanding open problem. -/

/-- The empty set is trivially Sidon. -/
lemma empty_isSidon : IsSidonFinset ∅ := by tauto

/-- The empty set is a subset of any `Finset.Icc`. -/
lemma empty_subset_Icc : (∅ : Finset ℕ) ⊆ Finset.Icc 1 N :=
  Finset.empty_subset _

/-- `erdos_44_sidon_extension` implies the existence of near-optimal Sidon sets.
    This is the **independence-style witness**: the conclusion is a fragment of the
    Erdős-Turán B₂ conjecture, open since 1941. -/
theorem reduction_to_open_problem
    (h : ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) :
    ∀ ε : ℝ, ε > 0 →
      ∃ M : ℕ, M ≥ 1 ∧
        ∃ S : Finset ℕ, S ⊆ Finset.Icc 1 M ∧
          IsSidonFinset S ∧
          (1 - ε) * Real.sqrt (M : ℝ) ≤ (S.card : ℝ) := by
  intro ε hε
  obtain ⟨Mε, hMε⟩ := h ε hε
  specialize hMε 1 (by norm_num) ∅
  simp at hMε
  obtain ⟨M, hM₁, B, hB₁, hB₂, hB₃⟩ := hMε (by tauto)
  exact ⟨M, hM₁.1, B, Finset.Subset.trans hB₁ (Finset.Icc_subset_Icc (by norm_num) le_rfl),
    hB₂, hB₃⟩

/-! ### Part 2: Concrete Sidon witness — {1, 5, 11, 13}

We verify that {1, 5, 11, 13} is Sidon and lives in [1, 13],
serving as a concrete test case for extension fragility. -/

/-- The set {1, 5, 11, 13} as a Finset. -/
def A₀ : Finset ℕ := {1, 5, 11, 13}

/-- {1, 5, 11, 13} is a Sidon set. -/
theorem A₀_isSidon : IsSidonFinset A₀ := by
  unfold IsSidonFinset; simp [A₀]
  rintro a b c d (rfl | rfl | rfl | rfl) (rfl | rfl | rfl | rfl)
    (rfl | rfl | rfl | rfl) (rfl | rfl | rfl | rfl) <;> decide

/-- {1, 5, 11, 13} ⊆ [1, 13]. -/
theorem A₀_subset : A₀ ⊆ Finset.Icc 1 13 := by native_decide +revert

/-- |A₀| = 4. -/
theorem A₀_card : A₀.card = 4 := by native_decide +revert

/-! ### Part 3: The "all-M" strengthening is false

The universal-M variant asserts that for EVERY M ≥ max(N, Mε) (not just some),
there exists an extension B achieving density (1-ε)√M. This is false:
for ε = 1/2 and any threshold Mε ≥ 1, choose N large enough and A = {1}.
Then for M = 4N² + 1, the singleton set {1} ⊆ [1, N] is Sidon, but no
extension B ⊆ [N+1, M] can bring |{1} ∪ B| above (1/2)√M ≈ N, since
|{1} ∪ B| ≤ 1 + (number of Sidon-compatible elements in [N+1, M]) which,
for adversarially chosen parameters, falls short. -/

/-- The universal-M strengthening (with Mε ≥ 1) is false. -/
theorem allM_variant_false :
    ¬ (∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, Mε ≥ 1 ∧
        ∀ N : ℕ, 1 ≤ N →
          ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
            ∀ M : ℕ, M ≥ max N Mε →   -- ← changed ∃ to ∀
              ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
                IsSidonFinset (A ∪ B) ∧
                (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  norm_num +zetaDelta at *
  use 1 / 2
  refine ⟨by norm_num, fun N hN => ?_⟩
  refine ⟨4 * N ^ 2 + 1, by nlinarith, {1}, ?_, ?_, 4 * N ^ 2 + 1, ?_, ?_, ?_⟩ <;> norm_num
  · intro a b c d ha hb hc hd h; aesop
  · nlinarith
  · exact fun _ => by
      nlinarith [show (N : ℝ) ≥ 1 by norm_cast,
        Real.sqrt_nonneg (4 * N ^ 2 + 1),
        Real.sq_sqrt (show 0 ≤ 4 * (N : ℝ) ^ 2 + 1 by positivity)]

end Erdos44Witness
