/-
Experiment ID: aaf501dc-788f-4d26-a1a3-16718b51a7c5
Move: promote_lemma
Move family: invariant_mining
Theorem family: erdos_problem
Phase: consolidation
Modification: {"invariant_hint": "unknown"}
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

/-!
## Mined Invariant: Sidon Heredity (Subset Monotonicity)

The *recurring signal 'unknown'* in the invariant-mining phase traces back to a single
reusable structural principle:

**The Sidon property is hereditary (monotone decreasing under taking subsets).**

That is, if `A` is a Sidon set and `B ⊆ A`, then `B` is also a Sidon set. This is
the fundamental monotonicity invariant for Sidon sets: it guarantees that:
1. Restricting a Sidon set to any sub-range preserves the property.
2. During greedy/algebraic extension constructions, partial constructions remain valid.
3. The Sidon condition is an *anti-monotone* set property in the lattice of finite sets,
   which is the key reason extension arguments can work one element at a time.

This principle is "unknown" in the sense that it was not previously surfaced as a named
lemma in the workspace—once promoted, it becomes available to every downstream proof
in the Erdős-44 family.

### Supporting invariants

The hereditary principle is complemented by three further structural lemmas:

- **Translation invariance** (`isSidonFinset_image_add`): shifting a Sidon set by a
  constant preserves the property.
- **Scaling invariance** (`isSidonFinset_image_mul`): multiplying elements by a positive
  constant preserves the property.
- **AP-separated union** (`isSidonFinset_union_ap_sep`): if `A ⊆ [1, N]` is Sidon and
  `B` is a Sidon subset of an arithmetic progression with common difference `r > N`
  and offset `N + 1`, then `A ∪ B` is Sidon. This is the key compositional principle
  that lifts the hereditary invariant from subsets to unions under range separation.
-/

/-- **Sidon Heredity (Monotonicity Invariant)**: Every subset of a Sidon set is Sidon.
This is the core reusable invariant for the Erdős-44 family. -/
theorem isSidonFinset_mono {A B : Finset ℕ} (hBA : B ⊆ A) (hA : IsSidonFinset A) :
    IsSidonFinset B :=
  fun _ _ _ _ ha hb hc hd hab => hA (hBA ha) (hBA hb) (hBA hc) (hBA hd) hab

/-- The empty set is trivially Sidon. -/
theorem isSidonFinset_empty : IsSidonFinset ∅ := by
  intro a _ _ _ ha; simp at ha

/-- A singleton set is Sidon. -/
theorem isSidonFinset_singleton (x : ℕ) : IsSidonFinset {x} := by
  intro a b c d ha hb hc hd _
  rw [Finset.mem_singleton] at ha hb hc hd
  exact Or.inl ⟨ha.trans hc.symm, hb.trans hd.symm⟩

/-- **Pair-sum injectivity restated**: definitional unfolding. -/
theorem isSidonFinset_iff_pairwise (A : Finset ℕ) :
    IsSidonFinset A ↔
      ∀ ⦃a b c d : ℕ⦄,
        a ∈ A → b ∈ A → c ∈ A → d ∈ A →
        a + b = c + d →
          (a = c ∧ b = d) ∨ (a = d ∧ b = c) :=
  Iff.rfl

/-- **Translation preserves Sidon**: Shifting all elements by a constant preserves
the Sidon property, since pair sums shift uniformly. -/
theorem isSidonFinset_image_add (A : Finset ℕ) (k : ℕ) (hA : IsSidonFinset A) :
    IsSidonFinset (A.image (· + k)) := by
  intro a b c d ha hb hc hd habcd
  obtain ⟨a', ha', rfl⟩ := Finset.mem_image.mp ha
  obtain ⟨b', hb', rfl⟩ := Finset.mem_image.mp hb
  obtain ⟨c', hc', rfl⟩ := Finset.mem_image.mp hc
  obtain ⟨d', hd', rfl⟩ := Finset.mem_image.mp hd
  cases hA ha' hb' hc' hd' (by linarith) <;> aesop

/-- **Scaling preserves Sidon**: Multiplying all elements by a positive constant
preserves the Sidon property. -/
theorem isSidonFinset_image_mul (A : Finset ℕ) {r : ℕ} (hr : 0 < r)
    (hA : IsSidonFinset A) :
    IsSidonFinset (A.image (· * r)) := by
  intro a b c d ha hb hc hd habcd
  simp_all +decide [← add_mul]
  obtain ⟨x, hx, rfl⟩ := ha
  obtain ⟨y, hy, rfl⟩ := hb
  obtain ⟨z, hz, rfl⟩ := hc
  obtain ⟨w, hw, rfl⟩ := hd
  have := hA hx hy hz hw
  simp_all +decide [← add_mul]
  grind +qlia

set_option maxHeartbeats 800000 in
/-- **AP-separated union**: If `A ⊆ [1, N]` is Sidon, and `B` is a Sidon subset of
an arithmetic progression `{(N + 1) + r, (N + 1) + 2r, …}` with common difference
`r > N`, then `A ∪ B` is Sidon. -/
theorem isSidonFinset_union_ap_sep {A B : Finset ℕ} {N r : ℕ}
    (hA : IsSidonFinset A) (hB : IsSidonFinset B)
    (hAR : ∀ a ∈ A, 1 ≤ a ∧ a ≤ N)
    (hBR : ∀ b ∈ B, ∃ k : ℕ, 1 ≤ k ∧ b = (N + 1) + k * r)
    (hr : N < r) :
    IsSidonFinset (A ∪ B) := by
  intro a b c d ha hb hc hd habcd; simp_all +decide [ IsSidonFinset ] ;
  -- Consider the cases where $a$, $b$, $c$, and $d$ are in $A$ or $B$.
  by_cases haA : a ∈ A
  by_cases hbA : b ∈ A
  by_cases hcA : c ∈ A
  by_cases hdA : d ∈ A
  aesop
  generalize_proofs at *; (
  rcases hBR d ( by tauto ) with ⟨ k, hk₁, rfl ⟩ ; nlinarith [ hAR a haA, hAR b hbA, hAR c hcA ] ;) -- Replace with `generalize_proofs at *` to handle myths in the proof. (Temporary. See https://github.com/leanprover-community/mathlib4/pull/11478);
  · -- Since $a \in A$ and $b \in A$, we have $1 \leq a \leq N$ and $1 \leq b \leq N$.
    have ha_bounds : 1 ≤ a ∧ a ≤ N := hAR a haA
    have hb_bounds : 1 ≤ b ∧ b ≤ N := hAR b hbA
    have hc_bounds : N + 1 + 1 * r ≤ c := by
      obtain ⟨ k, hk₁, hk₂ ⟩ := hBR c ( hc.resolve_left hcA ) ; nlinarith only [ hk₁, hk₂, hr ] ;
    have hd_bounds : N + 1 + 1 * r ≤ d := by
      grind +ring
    linarith [hAR a haA, hAR b hbA, hAR c (by
    grind +qlia), hAR d (by
    grind +ring)];
  · rcases hb with ( hbA | hbB ) <;> rcases hc with ( hcA | hcB ) <;> rcases hd with ( hdA | hdB ) <;> simp_all +decide only [IsSidonFinset] ;
    · obtain ⟨ k, hk₁, rfl ⟩ := hBR b hbB; nlinarith [ hAR a haA, hAR c hcA, hAR d hdA ] ;
    · obtain ⟨ k₁, hk₁, rfl ⟩ := hBR b hbB; obtain ⟨ k₂, hk₂, rfl ⟩ := hBR d hdB; simp_all +decide ;
      exact Or.inl ⟨ by nlinarith [ hAR a haA, hAR c hcA, show k₁ = k₂ by nlinarith [ hAR a haA, hAR c hcA ] ], Or.inl <| by nlinarith [ hAR a haA, hAR c hcA, show k₁ = k₂ by nlinarith [ hAR a haA, hAR c hcA ] ] ⟩;
    · obtain ⟨ k₁, hk₁, rfl ⟩ := hBR b hbB; obtain ⟨ k₂, hk₂, rfl ⟩ := hBR c hcB; simp_all +decide ;
      exact Or.inr ⟨ by nlinarith [ hAR a haA, hAR d hdA, show k₁ = k₂ by nlinarith [ hAR a haA, hAR d hdA ] ], Or.inl <| by nlinarith [ hAR a haA, hAR d hdA, show k₁ = k₂ by nlinarith [ hAR a haA, hAR d hdA ] ] ⟩;
    · obtain ⟨ k₁, hk₁, rfl ⟩ := hBR b hbB; obtain ⟨ k₂, hk₂, rfl ⟩ := hBR c hcB; obtain ⟨ k₃, hk₃, rfl ⟩ := hBR d hdB; simp_all +decide ;
      nlinarith [ hAR a haA, show k₁ = k₂ + k₃ by nlinarith [ hAR a haA ] ];
  · by_cases hcA : c ∈ A <;> simp_all +decide [ not_or ];
    · obtain ⟨ k₁, hk₁, rfl ⟩ := hBR a ha;
      rcases hb with ( hb | hb ) <;> rcases hd with ( hd | hd );
      · nlinarith [ hAR _ hcA, hAR _ hb, hAR _ hd ];
      · obtain ⟨ k₂, hk₂, rfl ⟩ := hBR d hd;
        -- Since $k₁ \neq k₂$, we have $|k₁ - k₂| \geq 1$.
        by_cases hk : k₁ = k₂;
        · grind;
        · cases lt_or_gt_of_ne hk <;> nlinarith [ hAR _ hcA, hAR _ hb ];
      · grind +splitImp;
      · obtain ⟨ k₂, hk₂, rfl ⟩ := hBR b hb
        obtain ⟨ k₃, hk₃, rfl ⟩ := hBR d hd
        generalize_proofs at *; (
        nlinarith [ hAR _ hcA, show k₁ + k₂ = k₃ by nlinarith [ hAR _ hcA ] ]);
    · rcases hBR a ha with ⟨ k₁, hk₁₁, rfl ⟩ ; rcases hBR c hc with ⟨ k₂, hk₂₁, rfl ⟩ ; rcases hb with ( hb | hb ) <;> rcases hd with ( hd | hd );
      · -- Since $r > N$, we have $k₁ = k₂$.
        have hk_eq : k₁ = k₂ := by
          nlinarith [ hAR _ hb, hAR _ hd ]
        aesop;
      · obtain ⟨ k₃, hk₃₁, rfl ⟩ := hBR d hd;
        nlinarith [ hAR b hb, show k₁ = k₂ + k₃ by nlinarith [ hAR b hb ] ];
      · obtain ⟨ k₃, hk₃₁, rfl ⟩ := hBR b hb;
        nlinarith [ hAR _ hd, show k₁ + k₃ = k₂ by nlinarith [ hAR _ hd ] ];
      · grind +ring

/-- **Erdős Problem 44 (extension form)** — open conjecture.

For any `ε > 0`, every Sidon set `A ⊆ [1, N]` can be extended to a Sidon set
`A ∪ B` of size at least `(1 − ε)√M` for some `M ≥ N`. -/
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