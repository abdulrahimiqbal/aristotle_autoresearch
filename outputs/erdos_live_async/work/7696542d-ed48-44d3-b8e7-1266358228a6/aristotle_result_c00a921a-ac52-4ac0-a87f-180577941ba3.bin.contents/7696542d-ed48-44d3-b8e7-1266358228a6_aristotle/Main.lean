/-
Experiment ID: 7696542d-ed48-44d3-b8e7-1266358228a6
Move: promote_lemma
Move family: legacy.promote_lemma
Theorem family: erdos_problem
Phase: consolidation
Modification: {"lemma_statement": "IsDivisionAntichain : (s : Finset ℕ) : Prop"}
-/

import Mathlib

/-- A divisibility antichain is a finite set of positive natural numbers
    in which no element divides any other distinct element. -/
def IsDivisionAntichain (s : Finset ℕ) : Prop :=
  ∀ a ∈ s, ∀ b ∈ s, a ∣ b → a = b

/-
PROBLEM
The interval (n/2, n] in ℕ, i.e. {⌊n/2⌋+1, ..., n}, forms a divisibility antichain.
    This is the key construction in Erdős-style arguments: if a ∣ b and both lie in (n/2, n],
    then b ≥ 2a > n, contradicting b ≤ n.

PROVIDED SOLUTION
Unfold IsDivisionAntichain. Take a, b in Finset.Icc (n/2+1) n with a ∣ b. Then a ≥ n/2+1, so if a ≠ b then b ≥ 2a ≥ 2(n/2+1) > n, contradicting b ≤ n. So a = b.
-/
theorem interval_upper_half_isAntichain (n : ℕ) :
    IsDivisionAntichain (Finset.Icc (n / 2 + 1) n) := by
  -- We must show that for any $a, b \in (n/2, n]$, if $a \mid b$ then $a = b$.
  intro a ha b hb hab; exact (by
  obtain ⟨ k, rfl ⟩ := hab;
  rcases k with ( _ | _ | k ) <;> norm_num at * ; nlinarith [ Nat.div_add_mod n 2, Nat.mod_lt n two_pos ] ;)

/-
PROBLEM
The "sharpest witness" for the boundary case: for n = 2, the set {2} is a divisibility
    antichain of size 1, equal to ⌈n/2⌉. Meanwhile the full interval {1, 2} is NOT a
    divisibility antichain since 1 ∣ 2, showing that interval-style coverage (using {1,...,n})
    cannot in general be upgraded to a divisibility antichain without restricting to the
    upper half.

PROVIDED SOLUTION
Unfold IsDivisionAntichain and push negation. We need to find a, b in {1,2} with a ∣ b and a ≠ b. Take a = 1, b = 2. Then 1 ∈ {1,2}, 2 ∈ {1,2}, 1 ∣ 2, and 1 ≠ 2.
-/
theorem boundary_witness_not_antichain :
    ¬ IsDivisionAntichain {1, 2} := by
  exact fun H => by have := H 1 ( by decide ) 2 ( by decide ) ; norm_num at this;

/-
PROBLEM
The promoted lemma: for any n ≥ 1, there exists a divisibility antichain
    contained in Finset.range (n+1) \ {0} (i.e. {1,...,n}).

PROVIDED SOLUTION
Given n ≥ 1, take s = {n}. Then s ⊆ Finset.Icc 1 n (since 1 ≤ n and n ≤ n), s is trivially a divisibility antichain (singleton), and s is nonempty.
-/
theorem promoted_lemma :
    ∀ n : ℕ, 0 < n → ∃ s : Finset ℕ, s ⊆ Finset.Icc 1 n ∧ IsDivisionAntichain s ∧ s.Nonempty := by
  exact fun n pos => ⟨ { n }, by simpa, fun a ha b hb hab => by aesop, Finset.singleton_nonempty _ ⟩