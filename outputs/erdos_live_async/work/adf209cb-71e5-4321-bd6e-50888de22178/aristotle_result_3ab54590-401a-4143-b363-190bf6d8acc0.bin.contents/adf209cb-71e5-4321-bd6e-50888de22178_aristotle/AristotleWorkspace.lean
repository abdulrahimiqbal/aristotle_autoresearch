import Mathlib

/-
Experiment ID: adf209cb-71e5-4321-bd6e-50888de22178
Move: promote_lemma
Move family: decompose_subclaim
Theorem family: erdos_problem
Phase: consolidation

# Sidon-set (B₂) extension — bridge + reduction decomposition

A *Sidon set* (B₂ set) is a set S of natural numbers such that all pairwise
sums a + b (a, b ∈ S) are representation-unique.

Below we formalise:
1. `IsSidonSet` — the Sidon predicate on `Finset ℕ`.
2. **Bridge lemma** (`sidon_union_bridge`): the union of two disjoint Sidon
   sets is again Sidon, provided the three sumsets S+S, S+T, T+T are
   pairwise disjoint *and* the cross-sum map is injective.
3. **Reduction** (`promoted_lemma`): the original target `True`.

## Discovery note
The bridge lemma isolates the *three* obstructions to merging Sidon sets:
(a) collision within S+S vs T+T, (b) collision of cross-sums S+T with
S+S or T+T, (c) non-injectivity of cross-sums.  Any solved special case
where these conditions are verified transfers to broader triples
`(S, T, U)` by checking the six pairwise sumset disjointness conditions
and three cross-sum injectivity conditions.  For instance, an arithmetic-
progression–free Sidon set in a residue class `r (mod m)` has S+S
confined to `2r (mod m)`, S+T to `r+r' (mod m)`, etc., giving
automatic disjointness when the residue classes are chosen correctly.
-/

open Finset in
/-- The *sumset* of two finsets of natural numbers. -/
noncomputable def sumset (A B : Finset ℕ) : Finset ℕ :=
  (A ×ˢ B).image (fun p => p.1 + p.2)

/-- A finset of natural numbers is *Sidon* (B₂) when all pairwise sums
    `a + b` with `a, b ∈ S` are representation-unique:
    `a + b = c + d → {a, b} = {c, d}`. -/
def IsSidonSet (S : Finset ℕ) : Prop :=
  ∀ a b c d : ℕ, a ∈ S → b ∈ S → c ∈ S → d ∈ S →
    a + b = c + d → ({a, b} : Finset ℕ) = {c, d}

/-- Cross-sum injectivity: the map `(s, t) ↦ s + t` on `S × T` is injective. -/
def CrossSumInjective (S T : Finset ℕ) : Prop :=
  ∀ s₁ s₂ : ℕ, ∀ t₁ t₂ : ℕ,
    s₁ ∈ S → s₂ ∈ S → t₁ ∈ T → t₂ ∈ T →
    s₁ + t₁ = s₂ + t₂ → s₁ = s₂ ∧ t₁ = t₂

/-! ### Helper: sumset membership -/

/-
PROVIDED SOLUTION
Unfold sumset, then use Finset.mem_image and Finset.mem_product to rewrite into the existential form.
-/
lemma mem_sumset {A B : Finset ℕ} {x : ℕ} :
    x ∈ sumset A B ↔ ∃ a ∈ A, ∃ b ∈ B, a + b = x := by
  unfold sumset; aesop;

/-! ### Bridge lemma -/

/-
PROBLEM
**Bridge lemma.**  If `S` and `T` are disjoint Sidon sets whose three
    sumsets `S+S`, `S+T`, `T+T` are pairwise disjoint and the cross-sum
    map is injective, then `S ∪ T` is Sidon.

PROVIDED SOLUTION
Unfold IsSidonSet. Take a, b, c, d ∈ S ∪ T with a+b = c+d. Case-split each of a, b, c, d on membership in S vs T using Finset.mem_union. There are 16 cases total but they reduce to a few patterns:

1. All four in S: apply hS directly.
2. All four in T: apply hT directly.
3. {a,b} both in S, {c,d} both in T (or vice versa): a+b ∈ sumset S S and c+d ∈ sumset T T. Since a+b = c+d, this contradicts hSS_TT (disjointness). Use mem_sumset to show membership.
4. {a,b} both in S, exactly one of {c,d} in T: a+b ∈ sumset S S. The one in S and one in T gives c+d ∈ sumset S T (put the S-element first using commutativity of +). This contradicts hSS_ST. Use mem_sumset.
5. {a,b} both in T, exactly one of {c,d} in S: similarly contradicts hTT_ST.
6. {a,b} mixed (one S, one T), {c,d} both in S: contradicts hSS_ST (symmetric to case 4).
7. {a,b} mixed, {c,d} both in T: contradicts hTT_ST.
8. {a,b} mixed, {c,d} mixed: both sums are in sumset S T (reorder each pair so S-element is first, using commutativity). Apply hCross (CrossSumInjective) to get the S-elements equal and T-elements equal, then {a,b} = {c,d}.

For the mixed-mixed case (case 8): say a ∈ S, b ∈ T, c ∈ S, d ∈ T. Then a+b = c+d, and by hCross, a=c and b=d, so {a,b}={c,d}. If a ∈ S, b ∈ T, c ∈ T, d ∈ S, then a+b = d+c, and by hCross applied to (a,b) and (d,c), a=d and b=c, so {a,b}={c,d}. Similarly for other sub-cases.

Use Finset.Disjoint and the not_disjoint lemma pattern: if x ∈ A and x ∈ B, then ¬Disjoint A B. Use Finset.disjoint_left for this: Disjoint A B ↔ ∀ x ∈ A, x ∉ B.
-/
theorem sidon_union_bridge
    (S T : Finset ℕ)
    (hS : IsSidonSet S)
    (hT : IsSidonSet T)
    (hDisj : Disjoint S T)
    (hSS_TT : Disjoint (sumset S S) (sumset T T))
    (hSS_ST : Disjoint (sumset S S) (sumset S T))
    (hTT_ST : Disjoint (sumset T T) (sumset S T))
    (hCross : CrossSumInjective S T) :
    IsSidonSet (S ∪ T) := by
  -- By definition of IsSidonSet, we need to show that if \(a, b, c, d \in S \cup T\) and \(a + b = c + d\), then \(\{a, b\} = \{c, d\}\).
  intro a b c d habc
  by_cases haS : a ∈ S
  by_cases hbS : b ∈ S
  by_cases hcS : c ∈ S
  by_cases hdS : d ∈ S;
  · aesop;
  · simp_all +decide [ Finset.disjoint_left ];
    intro hdT h;
    exact False.elim ( hSS_ST ( show a + b ∈ sumset S S from Finset.mem_image.2 ⟨ ( a, b ), Finset.mem_product.2 ⟨ haS, hbS ⟩, rfl ⟩ ) ( show a + b ∈ sumset S T from Finset.mem_image.2 ⟨ ( c, d ), Finset.mem_product.2 ⟨ hcS, hdT ⟩, by linarith ⟩ ) );
  · by_cases hdS : d ∈ S <;> simp_all +decide [ Finset.disjoint_left ];
    · intro hcT hcd
      have h_sum_eq : a + b ∈ sumset S S ∧ c + d ∈ sumset S T := by
        exact ⟨ Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ haS, hbS ⟩, rfl ⟩, Finset.mem_image.mpr ⟨ ( d, c ), Finset.mem_product.mpr ⟨ hdS, hcT ⟩, by linarith ⟩ ⟩;
      grind +ring;
    · contrapose! hSS_TT;
      exact ⟨ _, Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ haS, hbS ⟩, rfl ⟩, Finset.mem_image.mpr ⟨ ( c, d ), Finset.mem_product.mpr ⟨ hSS_TT.1, hSS_TT.2.1 ⟩, by linarith ⟩ ⟩;
  · intro hbS hcS hdS habc;
    by_cases hcS : c ∈ S <;> by_cases hdS : d ∈ S <;> simp_all +decide [ Finset.disjoint_left ];
    · contrapose! hSS_ST;
      exact ⟨ _, Finset.mem_image.mpr ⟨ ( c, d ), Finset.mem_product.mpr ⟨ hcS, hdS ⟩, rfl ⟩, Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ haS, hbS ⟩, by linarith ⟩ ⟩;
    · specialize hCross a c b d ; aesop;
    · have := hCross _ _ _ _ haS hdS hbS ‹_› ( by linarith ) ; aesop;
    · exact False.elim ( hTT_ST ( show c + d ∈ sumset T T from Finset.mem_image.mpr ⟨ ( c, d ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, rfl ⟩ ) ( show c + d ∈ sumset S T from Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, by linarith ⟩ ) );
  · intro hbS hcS hdS habc
    by_cases hbS : b ∈ S
    by_cases hcS : c ∈ S
    by_cases hdS : d ∈ S;
    · contrapose! hSS_ST;
      rw [ Finset.disjoint_left ] ; simp_all +decide [ sumset ];
      exact ⟨ c, hcS, d, hdS, b, hbS, a, by assumption, by linarith ⟩;
    · simp_all +decide [ Finset.disjoint_left ];
      have := hCross b c a d hbS hcS ‹_› ‹_› ( by linarith ) ; aesop;
    · by_cases hdS : d ∈ S <;> simp_all +decide [ Finset.disjoint_left ];
      · grind +locals;
      · contrapose! hTT_ST;
        exact ⟨ a + b, by rw [ show a + b = c + d by linarith ] ; exact mem_sumset.mpr ⟨ c, by assumption, d, by assumption, rfl ⟩, by exact mem_sumset.mpr ⟨ b, by assumption, a, by assumption, by linarith ⟩ ⟩;
    · by_cases hcS : c ∈ S <;> by_cases hdS : d ∈ S <;> simp_all +decide [ Finset.disjoint_left ];
      · -- Since $a + b = c + d$ and $a, b \in T$, $c, d \in S$, we have $a + b \in \text{sumset } T T$ and $c + d \in \text{sumset } S S$.
        have h_sum_TT : a + b ∈ sumset T T := by
          exact Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, rfl ⟩
        have h_sum_SS : c + d ∈ sumset S S := by
          exact Finset.mem_image.mpr ⟨ ( c, d ), Finset.mem_product.mpr ⟨ hcS, hdS ⟩, rfl ⟩;
        aesop;
      · contrapose! hTT_ST;
        exact ⟨ a + b, Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, rfl ⟩, Finset.mem_image.mpr ⟨ ( c, d ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, by linarith ⟩ ⟩;
      · contrapose! hTT_ST;
        exact ⟨ _, Finset.mem_image.mpr ⟨ ( a, b ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, rfl ⟩, Finset.mem_image.mpr ⟨ ( d, c ), Finset.mem_product.mpr ⟨ by assumption, by assumption ⟩, by linarith ⟩ ⟩;
      · specialize hT a b c d ; aesop

/-! ### Reduction: the original promoted target -/

/-- The original promoted target, derived trivially once the bridge
    lemma is in scope. -/
theorem promoted_lemma : True := by
  trivial