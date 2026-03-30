/-
Experiment ID: e34a4dd2-3645-4684-8541-5d124d12cde1
Move: reformulate
Move family: extremal_case
Theorem family: erdos_problem
Phase: consolidation
Modification: {"extremal_target": "extremal parameter boundary"}
-/

-- erdos family workspace
-- focus: extremal constructions, additive structure, and parameter boundary behavior
-- extremal sweep: extremal parameter boundary
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

/-!
## Extremal parameter boundary reformulation

The original Erdős Problem 44 conjectures that for every ε > 0, any Sidon subset of
[1, N] can be extended to a Sidon subset of [1, M] of size at least (1 − ε)√M.
The parameter ε > 0 controls how close the extended set's density can approach √M.

**Extremal boundary (ε → 0⁺):** The natural question is whether ε = 0 is achievable,
i.e., whether the coefficient 1 in front of √M is the sharp threshold. We show it is,
by proving the classical upper bound: any Sidon subset of [1, N] has at most
⌊√(2N)⌋ + 1 elements. This bound is a consequence of the fact that the |A|·(|A| − 1)
nonzero pairwise differences of a Sidon set are all distinct and lie in
{−(N−1), …, −1, 1, …, N−1}, a set of size 2(N − 1).

Consequently, even with an optimal extension, |A ∪ B| ≤ √(2M) + 1 for any Sidon
set in [1, M], so (1 − ε)√M ≤ √(2M) + 1 is necessary. This pins ε = 0 as the
boundary of the parameter range: one cannot improve (1 − ε) past 1.
-/

/-
PROBLEM
**Key counting lemma.** In a Sidon set `A ⊆ [1, N]`, the ordered differences
`a - b` for distinct `a, b ∈ A` are all distinct. Since they lie in the set
`{-(N-1), …, -1, 1, …, N-1}` of cardinality `2(N-1)`, we obtain the quadratic
bound `|A| * (|A| - 1) ≤ 2 * (N - 1)`.

Combined with simple algebra this yields `|A| ≤ ⌊√(2N)⌋ + 1`, the classical
extremal boundary for Sidon sets.

PROVIDED SOLUTION
The key idea: for a Sidon set A ⊆ [1, N], the function f : {(a, b) ∈ A × A | a ≠ b} → {-(N-1), ..., -1, 1, ..., N-1} given by f(a, b) = (a : ℤ) - (b : ℤ) is injective. This is because if a - b = c - d then a + d = b + c, and by the Sidon property {a, d} = {b, c}, which with a ≠ b forces a = c and b = d.

The domain has |A|*(|A|-1) elements, and the codomain has at most 2*(N-1) elements (nonzero integers in [-(N-1), N-1]). Therefore |A|*(|A|-1) ≤ 2*(N-1).

Approach: Define an injective function from ordered pairs of distinct elements of A to Fin (2*(N-1)+1) or to Icc (-(N-1 : ℤ)) (N-1) minus {0}, count the elements, and conclude. Alternatively, use the Finset.card_le_card_of_injOn approach with:
- The source: A.product A filtered to {(a,b) | a ≠ b}, which has card = A.card * (A.card - 1)
- An injection into Finset.Icc (-(N-1 : ℤ)) (N-1) \ {0} which has card ≤ 2*(N-1)
- The map sends (a, b) ↦ (a : ℤ) - (b : ℤ)

Key steps:
1. Build the source finset S = (A ×ˢ A).filter (fun p => p.1 ≠ p.2), show S.card = A.card * (A.card - 1)
2. Build the target finset T = Finset.Icc (-(N-1 : ℤ)) (N-1) \ {0}, show T.card ≤ 2*(N-1)
3. Show the map (a,b) ↦ (↑a - ↑b : ℤ) is injective on S (using IsSidonFinset)
4. Show the image lands in T (using A ⊆ [1,N])
5. Conclude by Finset.card_le_card_of_injOn
-/
theorem sidon_card_sq_le (N : ℕ) (hN : 1 ≤ N) (A : Finset ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    A.card * (A.card - 1) ≤ 2 * (N - 1) := by
  -- The set of differences $\{a - b \mid a, b \in A, a \neq b\}$ is a subset of $\{-(N-1), ..., -1, 1, ..., N-1\}$.
  have h_diff_subset : Finset.image (fun p : ℕ × ℕ => (p.1 : ℤ) - p.2) (Finset.offDiag A) ⊆ Finset.Icc (-(N-1 : ℤ)) (N-1) \ {0} := by
    grind;
  -- Since the differences are distinct, the cardinality of the set of differences is at most the cardinality of the set $\{-(N-1), ..., -1, 1, ..., N-1\}$.
  have h_diff_card : (Finset.image (fun p : ℕ × ℕ => (p.1 : ℤ) - p.2) (Finset.offDiag A)).card ≤ (Finset.Icc (-(N-1 : ℤ)) (N-1) \ {0}).card := by
    exact Finset.card_le_card h_diff_subset;
  -- The cardinality of the set $\{-(N-1), ..., -1, 1, ..., N-1\}$ is $2(N-1)$.
  have h_card_Icc : (Finset.Icc (-(N-1 : ℤ)) (N-1) \ {0}).card = 2 * (N - 1) := by
    rcases N with ( _ | _ | N ) <;> norm_num at *;
    rw [ Finset.card_sdiff ] ; norm_num ; ring;
    rw [ Finset.inter_eq_left.mpr ] <;> norm_num ; ring ; norm_cast ; aesop;
    linarith;
  rw [ Finset.card_image_of_injOn ] at h_diff_card;
  · simp_all +decide [ mul_tsub ];
  · intros p hp q hq h_eq;
    simp +zetaDelta at *;
    have := hS hp.1 hq.2.1 hp.2.1 hq.1 ( by linarith ) ; aesop;

/-
PROBLEM
**Extremal parameter boundary for Sidon sets.**
For any Sidon set `A ⊆ {1, …, N}`, the cardinality satisfies
`|A| ≤ √(2N) + 1`. This is the sharp extremal boundary: the coefficient `1`
in front of `√N` (equivalently `√(2N)` with the factor absorbed) cannot be
improved, and constitutes the `ε → 0⁺` limit of the Erdős Problem 44
parameter.

PROVIDED SOLUTION
Use `sidon_card_sq_le` to get A.card * (A.card - 1) ≤ 2 * (N - 1). From this, A.card * (A.card - 1) ≤ 2 * N. We want to show (A.card : ℝ) ≤ √(2N) + 1.

Let k = A.card. We have k * (k - 1) ≤ 2N (in ℕ). So (k - 1)² ≤ k * (k - 1) ≤ 2N, so k - 1 ≤ √(2N), so k ≤ √(2N) + 1.

More carefully: k * (k-1) ≤ 2N implies (k-1)² ≤ k*(k-1) ≤ 2N (since k-1 ≤ k for naturals). Then cast to ℝ: (↑(k-1))² ≤ 2*↑N. Take sqrt: ↑(k-1) ≤ √(2*↑N). So ↑k = ↑(k-1) + 1 ≤ √(2*↑N) + 1. Handle the case k = 0 separately (trivially true since 0 ≤ √(2N) + 1).
-/
theorem sidon_extremal_boundary (N : ℕ) (hN : 1 ≤ N) (A : Finset ℕ)
    (hA : A ⊆ Finset.Icc 1 N) (hS : IsSidonFinset A) :
    (A.card : ℝ) ≤ Real.sqrt (2 * N) + 1 := by
  -- From this, A.card * (A.card - 1) ≤ 2 * N. Let k = A.card. We have k * (k - 1) ≤ 2N.
  have h_card : (A.card : ℝ) * ((A.card : ℝ) - 1) ≤ 2 * N := by
    -- By the lemma, we have A.card * (A.card - 1) ≤ 2 * (N - 1).
    have h_card_sq_le : A.card * (A.card - 1) ≤ 2 * (N - 1) := by
      exact sidon_card_sq_le N hN A hA hS;
    rcases N with ( _ | _ | N ) <;> norm_num at *;
    · aesop;
    · cases A_card : A.card <;> norm_num [ A_card ] at * ; nlinarith;
      norm_cast ; linarith;
  nlinarith [ Real.sqrt_nonneg ( 2 * N : ℝ ), Real.mul_self_sqrt ( show 0 ≤ 2 * ( N : ℝ ) by positivity ) ]

end Erdos44