# Summary of changes
## Summary

### Mined Invariant: Sidon Heredity (Subset Monotonicity)

The recurring signal **'unknown'** in the invariant-mining metadata corresponds to a fundamental structural principle that was not previously surfaced as a named lemma in the workspace:

> **The Sidon property is hereditary (monotone decreasing under taking subsets):** if `A` is a Sidon set and `B ⊆ A`, then `B` is also Sidon.

This is the core reusable monotonicity invariant for the Erdős-44 family. It ensures that:
1. Restricting a Sidon set to any sub-range preserves the property.
2. Greedy/algebraic extension constructions maintain validity at each step.
3. The Sidon condition is anti-monotone in the lattice of finite sets.

### Proved Lemmas (all sorry-free)

Seven lemmas were proved in `Main.lean`:

1. **`isSidonFinset_mono`** — The hereditary invariant (every subset of a Sidon set is Sidon).
2. **`isSidonFinset_empty`** — The empty set is Sidon.
3. **`isSidonFinset_singleton`** — Every singleton is Sidon.
4. **`isSidonFinset_iff_pairwise`** — Definitional unfolding of the Sidon condition.
5. **`isSidonFinset_image_add`** — Translation preserves the Sidon property.
6. **`isSidonFinset_image_mul`** — Scaling by a positive constant preserves the Sidon property.
7. **`isSidonFinset_union_ap_sep`** — **AP-separated union criterion**: if `A ⊆ [1, N]` is Sidon and `B` is a Sidon subset of an arithmetic progression with common difference `r > N` and offset `N + 1`, then `A ∪ B` is Sidon. This is the key compositional principle that lifts the hereditary invariant from subsets to unions.

### Remaining Sorry

**`erdos_44_sidon_extension`** — This is a formalization of **Erdős Problem 44** in its extension form: for any `ε > 0`, every Sidon set `A ⊆ [1, N]` can be extended to a Sidon set `A ∪ B` of near-optimal size `(1 − ε)√M`. This is a **known open conjecture** in additive combinatorics. Proving it requires constructing dense Sidon sets (via Singer/Bose–Chowla perfect difference sets) and resolving cross-sum conflicts between the original set and the extension — a combination that remains unresolved in the mathematical literature. Multiple proof strategies were attempted, but none succeeded for the case `0 < ε < 1`.

### Build Configuration

The `lakefile.toml` was replaced with a `lakefile.lean` to match the Lake v5 format expected by the project's Lean 4.28.0 toolchain.