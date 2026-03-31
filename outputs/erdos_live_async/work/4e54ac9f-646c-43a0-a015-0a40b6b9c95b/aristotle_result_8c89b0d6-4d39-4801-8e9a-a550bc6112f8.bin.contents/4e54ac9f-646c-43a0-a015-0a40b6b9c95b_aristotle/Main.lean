/-
Experiment ID: 4e54ac9f-646c-43a0-a015-0a40b6b9c95b
Move: counterexample_mode
Move family: legacy.counterexample_mode
Theorem family: erdos_problem
Phase: consolidation
Modification: {"attempt": 26, "target": "most_fragile_variant"}
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

/-- The singleton set is Sidon. -/
lemma isSidonFinset_singleton (x : ℕ) : IsSidonFinset {x} := by
  intro a b c d ha hb hc hd _
  simp [Finset.mem_singleton] at ha hb hc hd
  subst ha; subst hb; subst hc; subst hd
  left; exact ⟨rfl, rfl⟩

/-
PROBLEM
In a Sidon set, the difference map on off-diagonal pairs is injective: if
    a - b = c - d (as integers) with a ≠ b and c ≠ d, then a = c and b = d.

PROVIDED SOLUTION
If (a,b) and (c,d) are in A.offDiag with a-b = c-d (as integers), then a+d = b+c (rearranging). Since a,b,c,d ∈ A and a+d = b+c, by IsSidonFinset we get (a=b ∧ d=c) ∨ (a=c ∧ d=b). The first case contradicts a ≠ b (from offDiag). So a=c and d=b, giving (a,b) = (c,d).
-/
lemma sidon_diff_injective (A : Finset ℕ) (hSidon : IsSidonFinset A) :
    ∀ p q : ℕ × ℕ, p ∈ A.offDiag → q ∈ A.offDiag →
      (p.1 : ℤ) - p.2 = (q.1 : ℤ) - q.2 → p = q := by
  intro p q hp hq h_eq;
  -- By rearranging $p.1 - p.2 = q.1 - q.2$, we get $p.1 + q.2 = p.2 + q.1$.
  have h_sum : p.1 + q.2 = p.2 + q.1 := by
    grind;
  have := hSidon ( Finset.mem_offDiag.mp hp |>.1 ) ( Finset.mem_offDiag.mp hq |>.2.1 ) ( Finset.mem_offDiag.mp hp |>.2.1 ) ( Finset.mem_offDiag.mp hq |>.1 ) h_sum; aesop;

/-
PROBLEM
The off-diagonal differences of a Sidon subset of [1, N] land in the open
    interval (-(N : ℤ), N).

PROVIDED SOLUTION
Since p ∈ A.offDiag, p.1 ∈ A and p.2 ∈ A and p.1 ≠ p.2. Since A ⊆ Finset.Icc 1 N, we have 1 ≤ p.1 ≤ N and 1 ≤ p.2 ≤ N. So p.1 - p.2 > -(N:ℤ) (since p.1 ≥ 1 > 0 and p.2 ≤ N) and p.1 - p.2 < N (since p.1 ≤ N and p.2 ≥ 1 > 0). So the difference is in Finset.Ioo (-(N:ℤ)) N.
-/
lemma sidon_diff_mem_Ioo (A : Finset ℕ) (N : ℕ) (hA : A ⊆ Finset.Icc 1 N)
    (p : ℕ × ℕ) (hp : p ∈ A.offDiag) :
    (p.1 : ℤ) - p.2 ∈ Finset.Ioo (-(N : ℤ)) N := by
  grind

/-
PROBLEM
The core counting bound: for a Sidon subset A of [1, N], the number of
    off-diagonal pairs is at most 2N - 1.

PROVIDED SOLUTION
The map f : A.offDiag → Finset.Ioo (-(N:ℤ)) N defined by f(a,b) = a - b is injective (by sidon_diff_injective) and maps into Finset.Ioo (-(N:ℤ)) N (by sidon_diff_mem_Ioo). So A.offDiag.card ≤ (Finset.Ioo (-(N:ℤ)) N).card. We know A.offDiag.card = A.card * (A.card - 1) (this is Finset.card_offDiag). And (Finset.Ioo (-(N:ℤ)) N).card = 2*N - 1 (it's the integers from -(N-1) to N-1, which is 2N-1 elements). So A.card*(A.card-1) ≤ 2*N - 1.

Use Finset.card_le_card_of_injOn with the function fun p => (p.1 : ℤ) - p.2 and Finset.Ioo (-(N:ℤ)) N as the target.
-/
lemma sidon_offDiag_card_le (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    A.card * (A.card - 1) ≤ 2 * N - 1 := by
  have h_off_diag : Finset.card (A.offDiag) ≤ Finset.card (Finset.Ioo (-(N : ℤ)) N) := by
    have h_inj_card : Finset.card (Finset.image (fun p => (p.1 : ℤ) - p.2) (A.offDiag)) ≤ Finset.card (Finset.Ioo (-↑N : ℤ) ↑N) := by
      exact Finset.card_le_card fun x hx => by rcases Finset.mem_image.mp hx with ⟨ p, hp, rfl ⟩ ; exact sidon_diff_mem_Ioo A N hA p hp;
    rwa [ Finset.card_image_of_injOn ] at h_inj_card;
    exact fun p hp q hq hpq => sidon_diff_injective A hSidon p q hp hq hpq;
  simp_all +decide [ mul_tsub ];
  grind

/-
PROBLEM
Sidon set cardinality upper bound: |A| < 2√N for any Sidon A ⊆ [1, N].
    This follows from the off-diagonal counting bound.

PROVIDED SOLUTION
From sidon_offDiag_card_le, A.card * (A.card - 1) ≤ 2*N - 1. Let k = A.card. Then k*(k-1) ≤ 2*N - 1 < 2*N. We want k < 2*sqrt(N), i.e., k^2 < 4*N. From k*(k-1) ≤ 2*N - 1, we get k^2 - k ≤ 2*N - 1, so k^2 ≤ 2*N - 1 + k ≤ 2*N + k. Since k ≤ N (A ⊆ Finset.Icc 1 N has N elements), k^2 ≤ 2*N + N = 3*N < 4*N for N ≥ 1. So k^2 < 4*N, meaning k < 2*sqrt(N). Cast to reals and use Real.sqrt properties.
-/
theorem sidon_card_lt_two_sqrt (A : Finset ℕ) (N : ℕ) (hN : 1 ≤ N)
    (hA : A ⊆ Finset.Icc 1 N) (hSidon : IsSidonFinset A) :
    (A.card : ℝ) < 2 * Real.sqrt N := by
  -- By the off-diagonal counting bound, we have $A.card * (A.card - 1) ≤ 2 * (N : ℕ) - 1$.
  have bound : (A.card : ℝ) * ((A.card : ℝ) - 1) ≤ 2 * (N : ℝ) - 1 := by
    -- By Lemma~\ref{lem:sidon_off-diag}, we know that $\mid A \mid * (\mid A \mid - 1) \leq 2 * (N : ℕ) - 1$.
    have := @sidon_offDiag_card_le A N hN hA hSidon;
    norm_cast;
    grind;
  nlinarith only [ bound, show 1 ≤ Real.sqrt N from Real.le_sqrt_of_sq_le ( by norm_cast ), Real.sq_sqrt <| Nat.cast_nonneg N ]

/-! ## Counterexample to the most fragile variant

The "most fragile variant" of the Erdős Problem 44 conjecture replaces
the factor `(1 - ε)` with the constant `2`. This variant asserts that any
Sidon set can be extended to one of cardinality ≥ 2√M. We show this is false
using the Sidon cardinality upper bound: any Sidon subset of [1, M] has
fewer than 2√M elements, making the extension bound unachievable. -/

/-
PROBLEM
The strengthened ("most fragile") variant of Erdős Problem 44, with
    factor 2 instead of (1-ε), is false.

PROVIDED SOLUTION
Push the negation through: it suffices to find N ≥ 1, A Sidon ⊆ [1,N], and show for all M ≥ N, B ⊆ [N+1, M], if A ∪ B is Sidon then |A ∪ B| < 2√M. Take N = 1, A = {1} (Sidon by isSidonFinset_singleton). For any M ≥ 1 and B ⊆ [2, M], A ∪ B ⊆ [1, M]. If A ∪ B is Sidon, then by sidon_card_lt_two_sqrt, |A ∪ B| < 2√M. So 2√M ≤ |A ∪ B| is impossible. Use linarith or exact not_le.mpr.
-/
theorem erdos_44_fragile_false :
    ¬ (∀ N : ℕ, 1 ≤ N →
      ∀ A : Finset ℕ, A ⊆ Finset.Icc 1 N → IsSidonFinset A →
        ∃ M : ℕ, M ≥ N ∧
          ∃ B : Finset ℕ, B ⊆ Finset.Icc (N + 1) M ∧
            IsSidonFinset (A ∪ B) ∧
            2 * Real.sqrt (M : ℝ) ≤ ((A ∪ B).card : ℝ)) := by
  push_neg;
  use 1;
  refine' ⟨ le_rfl, _ ⟩;
  refine' ⟨ { 1 }, _, _, _ ⟩ <;> norm_num;
  · exact isSidonFinset_singleton 1;
  · intro M hM B hB hSidon;
    convert sidon_card_lt_two_sqrt ( insert 1 B ) M hM _ hSidon;
    grind

/-! ## Original conjecture (open problem)

The original Erdős Problem 44 conjecture, with factor `(1 - ε)`, remains an
open problem in additive combinatorics. We state it here for completeness. -/

/-- A workspace-local Lean 4 stub for Erdős Problem 44. The formal-conjectures repo
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

end Erdos44