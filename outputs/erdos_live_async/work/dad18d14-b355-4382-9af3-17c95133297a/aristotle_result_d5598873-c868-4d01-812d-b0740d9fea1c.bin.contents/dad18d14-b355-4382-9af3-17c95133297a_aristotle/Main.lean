/-
Experiment ID: dad18d14-b355-4382-9af3-17c95133297a
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 33, "target": "minimal_variant"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
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
## Minimal variant: linear density bound

The "minimal variant" strengthens the conclusion of Erdős Problem 44 by replacing
the sub-linear `(1 - ε) * √M` density bound with the linear bound `(1 - ε) * M`.
This asks whether Sidon sets can achieve density proportional to the interval length,
rather than merely proportional to its square root.

We show this minimal variant is **false**: a counting argument proves that any Sidon
set in `[1, M]` has at most `2√M` elements (pair sums are distinct and bounded),
so a linear density requirement fails for large `M`.
-/

/-- **Minimal variant** of Erdős Problem 44: replace `√M` with `M` in the density bound.
This strengthening asks whether Sidon extensions can achieve linear density. -/
def erdos_44_minimal_variant : Prop :=
    ∀ ε : ℝ, ε > 0 →
      ∃ Mε : ℕ, ∀ N : ℕ, 1 ≤ N →
        ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
          ∃ M : ℕ, M ≥ max N Mε ∧
            ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
              IsSidonFinset (A ∪ B) ∧
              (1 - ε) * (M : ℝ) ≤ ((A ∪ B).card : ℝ)

/-!
### Sidon set cardinality bound

The key ingredient for the counterexample: in a Sidon set `A ⊆ [1, M]`, the
pair-sums `a + b` (as unordered pairs with repetition) are all distinct and lie
in `{2, …, 2M}`. Since there are `|A|(|A|+1)/2` such sums and only `2M - 1`
possible values, we get `|A|(|A|+1)/2 ≤ 2M - 1`, hence `|A|² ≤ 4M`.
-/

/-
The pair sums of a Sidon set are an injection from unordered pairs into ℕ.
-/
lemma sidon_pairsum_injective (A : Finset ℕ) (hS : IsSidonFinset A) :
    ∀ a b c d : ℕ, a ∈ A → b ∈ A → c ∈ A → d ∈ A →
      a ≤ b → c ≤ d → a + b = c + d → a = c ∧ b = d := by
  -- Apply the definition of IsSidonFinset to the given equality.
  intros a b c d ha hb hc hd hab hcd hsum
  have h_eq : (a = c ∧ b = d) ∨ (a = d ∧ b = c) := by
    exact hS ha hb hc hd hsum;
  grind

/-
A Sidon set in `[1, M]` has at most `2 * √M` elements, more precisely
`card(A)^2 ≤ 4 * M`. This follows from counting distinct pair sums.
-/
lemma sidon_card_sq_le (A : Finset ℕ) (M : ℕ) (hA : A ⊆ Finset.Icc 1 M)
    (hS : IsSidonFinset A) : A.card ^ 2 ≤ 4 * M := by
  -- The number of such pairs is at least $|A|^2 / 2$ (actually $|A|(|A|+1)/2$).
  have h_pair_count : Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A)) ≥ A.card * (A.card + 1) / 2 := by
    have h_pair_count : Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A)) + Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 > p.2) (A ×ˢ A)) = A.card * A.card := by
      rw [ Finset.card_filter, Finset.card_filter ];
      rw [ ← Finset.sum_add_distrib, Finset.sum_congr rfl fun x hx => by aesop, Finset.sum_const, Finset.card_product ] ; norm_num;
    have h_pair_count_symm : Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 > p.2) (A ×ˢ A)) = Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 < p.2) (A ×ˢ A)) := by
      rw [ Finset.card_filter, Finset.card_filter ];
      rw [ Finset.sum_product, Finset.sum_product ];
      rw [ Finset.sum_comm ];
    have h_pair_count_symm : Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 < p.2) (A ×ˢ A)) + Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 = p.2) (A ×ˢ A)) = Finset.card (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A)) := by
      rw [ ← Finset.card_union_of_disjoint ];
      · congr with p ; simp +decide [ le_iff_lt_or_eq ];
        tauto;
      · exact Finset.disjoint_filter.mpr fun _ _ _ _ => by linarith;
    exact Nat.div_le_of_le_mul <| by linarith [ show Finset.card ( Finset.filter ( fun p : ℕ × ℕ => p.1 = p.2 ) ( A ×ˢ A ) ) = A.card from by rw [ show Finset.filter ( fun p : ℕ × ℕ => p.1 = p.2 ) ( A ×ˢ A ) = Finset.image ( fun x => ( x, x ) ) A by ext ⟨ x, y ⟩ ; aesop ] ; rw [ Finset.card_image_of_injective ] ; aesop_cat ] ;
  -- The number of such pairs is at most $2M - 1$.
  have h_pair_bound : Finset.card (Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A))) ≤ 2 * M - 1 := by
    have h_pair_bound : Finset.image (fun (p : ℕ × ℕ) => p.1 + p.2) (Finset.filter (fun (p : ℕ × ℕ) => p.1 ≤ p.2) (A ×ˢ A)) ⊆ Finset.Icc 2 (2 * M) := by
      grind;
    exact le_trans ( Finset.card_le_card h_pair_bound ) ( by simp +arith +decide );
  rw [ Finset.card_image_of_injOn ] at h_pair_bound;
  · rcases M with ( _ | _ | M ) <;> simp_all +decide;
    · aesop;
    · grind;
  · intro p hp q hq; have := @sidon_pairsum_injective A hS p.1 p.2 q.1 q.2; aesop;

/-
**The minimal variant is false.** For `ε = 1/2`, any Sidon set in `[1, M]`
has at most `2√M < M/2` elements for `M ≥ 17`, so the linear density bound fails.
-/
theorem erdos_44_minimal_variant_false : ¬ erdos_44_minimal_variant := by
  intro h;
  have := @h ( 1 / 4 ) ( by norm_num );
  obtain ⟨ Mε, hMε ⟩ := this;
  obtain ⟨ M, hM₁, B, hB₁, hB₂, hB₃ ⟩ := hMε ( Max.max Mε 17 ) ( by norm_num ) { 1 } ( by norm_num ) ( by unfold IsSidonFinset; aesop );
  -- Since $A = \{1\}$ and $B \subseteq [N+1, M]$, we have $A \cup B \subseteq [1, M]$.
  have h_union_subset : ({1} ∪ B) ⊆ Finset.Icc 1 M := by
    grind +splitIndPred;
  -- By the properties of the Sidon set, we have $|A \cup B|^2 \leq 4M$.
  have h_card_sq : (({1} ∪ B).card : ℝ) ^ 2 ≤ 4 * M := by
    exact_mod_cast sidon_card_sq_le _ _ h_union_subset hB₂;
  nlinarith [ show ( M : ℝ ) ≥ 17 by norm_cast; linarith [ le_max_left ( max Mε 17 ) Mε, le_max_right ( max Mε 17 ) Mε, le_max_left Mε 17, le_max_right Mε 17 ] ]

end Erdos44