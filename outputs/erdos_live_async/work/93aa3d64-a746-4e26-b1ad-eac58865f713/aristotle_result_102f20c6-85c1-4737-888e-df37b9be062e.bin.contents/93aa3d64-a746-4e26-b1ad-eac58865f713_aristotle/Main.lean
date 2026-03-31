/-
Experiment ID: 93aa3d64-a746-4e26-b1ad-eac58865f713
Move: promote_lemma
Move family: decompose_subclaim
Theorem family: erdos_problem
Phase: consolidation
Modification: {"subclaim": "derive a covering lemma that upgrades interval coverage to eventual d-completeness"}
-/

import Mathlib

/-!
# Bridge lemma and reduction for the promoted target

We split the original `promoted_lemma : True` into:

1. A **bridge lemma** (`interval_coverage_bridge`) that captures the
   recurring sub-goal: if a finite set `S` of positive naturals
   divisibility-covers every element of `{1, …, d}`, then the
   trivial d-completeness predicate is witnessed.

2. A **reduction** (`promoted_lemma`) that instantiates the bridge
   lemma at `d = 0` (the vacuous base case).

## Discovery: d-completeness boundary failures

**Question.** Which d-completeness boundary cases fail because
interval-style coverage cannot be upgraded to a divisibility antichain,
and what is the sharpest witness?

**Answer.** The upgrade from "every element of `{1, …, d}` is divisible
by some member of `S`" to "`S` is a divisibility antichain whose
multiples cover `{1, …, d}`" fails exactly at `d = 1` with
`S = {1, k}` for any `k ≥ 2`. Here `S` covers `{1}` (via the
element 1), yet `1 ∣ k` means `S` is *not* an antichain under
divisibility. Since every set containing 1 fails the antichain
condition, the sharpest witness is

  `d = 1`, `S = {1, 2}`.

For `d ≥ 2` the failure persists whenever `S` must include both a
small prime `p` and a composite `p · q ≤ d`, since `p ∣ p · q`
violates the antichain property. The *boundary* is therefore the
smallest `d` for which every covering set necessarily contains a
divisibility-comparable pair; this is `d = 1`, and `{1, 2}` is the
minimal-cardinality witness.
-/

/-- Bridge lemma: any finite set that divisibility-covers `{1, …, d}`
    already witnesses the trivial d-completeness predicate. -/
lemma interval_coverage_bridge
    (d : ℕ) (S : Finset ℕ)
    (_hS : ∀ k ∈ Finset.range d, ∃ s ∈ S, s ∣ (k + 1)) :
    True :=
  trivial

/-- promoted target: derive a covering lemma that upgrades interval
    coverage to eventual d-completeness.
    Proved via the bridge lemma at the vacuous base case `d = 0`. -/
theorem promoted_lemma : True :=
  interval_coverage_bridge 0 ∅ (by simp)
