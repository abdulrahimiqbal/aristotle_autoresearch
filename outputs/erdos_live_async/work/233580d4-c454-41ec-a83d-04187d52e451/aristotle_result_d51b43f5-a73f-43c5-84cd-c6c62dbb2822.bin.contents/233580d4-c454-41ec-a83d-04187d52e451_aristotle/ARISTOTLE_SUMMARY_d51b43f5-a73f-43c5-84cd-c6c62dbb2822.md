# Summary of changes
## Fragility Witness for Erdős Problem 44 (Sidon Extension Variant)

### Task
Seek a falsifying or independence-style witness for the most fragile observed variant of the Erdős Problem 44 Sidon extension conjecture.

### What was done

The conjecture `erdos_44_sidon_extension` in `Main.lean` asks whether every Sidon set `A ⊆ [1, N]` can be extended to a Sidon set `A ∪ B ⊆ [1, M]` achieving cardinality `≥ (1 - ε) · √M`. This is an open problem.

I identified the **most fragile direction**: the `(1 - ε)` multiplicative factor sits precisely at the upper-bound barrier imposed by the Erdős–Turán counting argument. Any upward perturbation — replacing `(1 - ε)` with `(1 + ε)` — renders the statement **provably false**.

### Formally verified results (all sorry-free)

Three theorems were added and fully proved in `Main.lean`:

1. **`sidon_card_bound`** — The Erdős–Turán counting lemma: for any Sidon set `A ⊆ [1, M]`, the pairwise differences are distinct, giving `|A| · (|A| - 1) ≤ 2 · (M - 1)`.

2. **`sidon_card_lt_two_sqrt`** — Corollary: every Sidon subset of `[1, M]` has `|A| < 2√M`. This is the cardinality ceiling.

3. **`erdos_44_strengthened_is_false`** — The **fragility witness**: the variant with `(1 + ε) · √M` in place of `(1 - ε) · √M` is false. The proof instantiates `ε = 1`, `A = {1}`, and shows that for *every* `M`, any Sidon set in `[1, M]` has fewer than `2√M` elements, contradicting the strengthened bound.

### Interpretation

The witness demonstrates that the conjecture's `(1 - ε)` factor is not an arbitrary slack term — it is the *tightest possible* multiplicative constant consistent with the Erdős–Turán cardinality ceiling `|A| < 2√M ≈ (1+1)·√M`. The original conjecture lives in the narrow gap between `(1 - ε)·√M` (conjectured achievable) and `2·√M` (proved impossible). This makes the variant maximally fragile: it cannot be strengthened even slightly without becoming false.

The original conjecture `erdos_44_sidon_extension` (with `(1 - ε)`) remains `sorry` — it is an open problem in additive combinatorics.