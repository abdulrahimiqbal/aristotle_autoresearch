/-
Experiment ID: 4ac0f00d-2b93-42ee-a1a6-ebcfd6efbcf4
Move: reformulate
Move family: extremal_case
Theorem family: erdos_problem
Phase: consolidation
Modification: {"extremal_target": "erdos_44_sidon_extension"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- extremal sweep: boundary‑case reformulation of the Erdős Problem 44 Sidon extension
import Mathlib

noncomputable section

namespace Erdos44

open Finset

/-- A finite set of natural numbers is Sidon if equal pair sums are trivial up to
reordering of the summands. -/
def IsSidonFinset (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄,
    a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a + b = c + d →
      (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-! ### Original conjecture (open problem — commented out for reference)

The full Erdős Problem 44 conjectures that any Sidon subset of `[1, N]` can be
extended to a Sidon set in `[1, M]` whose size is at least `(1 - ε) √M` for every
`ε > 0` and sufficiently large `M`.  This is currently open.

```
theorem erdos_44_sidon_extension :
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ) := by
  sorry
```
-/

/-! ## Extremal / boundary‑case reformulation

In the limit `ε → 0` the conjecture would give Sidon sets of size approaching
`√M`.  The **complementary** fact is that Sidon sets *cannot* exceed `2√N` elements
inside `[1, N]`:  we prove `|A|² ≤ 4 N`.

Together the two bounds pin down the correct order of magnitude as `Θ(√N)` and
explain why the factor `(1 - ε)` in the original conjecture is unavoidable.

### Proof sketch

Consider the `|A|²` ordered pairs `(a, b) ∈ A × A` and the addition map
`σ(a, b) = a + b`.

1. **Fibre bound** — the Sidon property forces every fibre
   `σ⁻¹(s) ∩ (A × A)` to have at most **2** elements (a pair and its transpose).
2. **Image bound** — since `1 ≤ a, b ≤ N` every sum lands in `{2, …, 2N}`,
   an interval of at most `2N` values.
3. By `Finset.card_le_mul_card_image` we obtain
   `|A|² ≤ 2 · (2N) = 4N`. -/

/-- Sidon fibre bound: for a Sidon set `A`, at most two ordered pairs in `A ×ˢ A`
share the same sum. -/
lemma sidon_fiber_le_two (A : Finset ℕ) (hS : IsSidonFinset A) (s : ℕ) :
    ((A ×ˢ A).filter (fun p => p.1 + p.2 = s)).card ≤ 2 := by
  by_cases h : ∃ p ∈ A ×ˢ A, p.1 + p.2 = s
  · obtain ⟨⟨a, b⟩, hp, rfl⟩ := h
    refine' le_trans (Finset.card_le_card _) _
    exact {(a, b), (b, a)}
    · intro p hp; specialize hS; aesop
    · exact Finset.card_insert_le _ _
  · rw [Finset.card_eq_zero.mpr] <;> aesop

/-- Every pairwise sum of elements in `A ⊆ [1, N]` lies in `Finset.range (2N + 1)`. -/
lemma sum_mem_range (N : ℕ) (A : Finset ℕ) (hA : A ⊆ Finset.Icc 1 N)
    (p : ℕ × ℕ) (hp : p ∈ A ×ˢ A) :
    p.1 + p.2 ∈ Finset.range (2 * N + 1) := by
  grind +qlia

/-- **Extremal / boundary‑case theorem.**
Every Sidon subset of `[1, N]` satisfies `|A|² ≤ 4N`.
This is the upper‑bound counterpart to the Erdős Problem 44 conjecture and shows
that the conjectured size `(1 − ε)√M` is of the right order. -/
theorem erdos_44_sidon_upper_bound (N : ℕ) (A : Finset ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    A.card ^ 2 ≤ 4 * N := by
  have h_prod : (A ×ˢ A).card ≤ 2 * (Finset.image (fun p => p.1 + p.2) (A ×ˢ A)).card := by
    convert Finset.card_le_mul_card_image_of_maps_to _ _ _ using 1
    exacts [by infer_instance, fun p => p.1 + p.2, fun p hp => Finset.mem_image_of_mem _ hp,
      fun b hb => by rcases Finset.mem_image.mp hb with ⟨p, hp, rfl⟩;
                     exact sidon_fiber_le_two A hS _]
  have image_subset :
      Finset.image (fun p : ℕ × ℕ => p.1 + p.2) (A ×ˢ A) ⊆ Finset.Icc 2 (2 * N) := by
    grind +splitImp
  have := Finset.card_le_card image_subset
  simp_all +decide [sq, two_mul]
  omega

end Erdos44
