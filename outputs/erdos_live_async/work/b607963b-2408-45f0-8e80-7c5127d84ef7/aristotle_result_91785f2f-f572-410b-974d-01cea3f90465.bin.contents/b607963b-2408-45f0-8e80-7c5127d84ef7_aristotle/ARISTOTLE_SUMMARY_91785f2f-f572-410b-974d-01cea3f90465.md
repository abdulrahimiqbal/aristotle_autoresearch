# Summary of changes
## Falsifying Witness for the Most Fragile Variant of Erdős Problem 44

### Identifying the fragile variant

The original theorem `erdos_44_sidon_extension` requires extending any Sidon set to achieve density `(1 - ε) * √M`. The **most fragile observed variant** is obtained by replacing the density bound `(1 - ε) * √M` with `(√2 + ε) * √M`, pushing the target density past the theoretical counting-bound ceiling of `√(2M)`.

### The counting bound

The key mathematical insight is the **Sidon counting bound**: for any Sidon set `A ⊆ [1, M]`, the positive differences `a - b` (for `a > b` in `A`) are all distinct and lie in `{1, …, M-1}`. This forces:

  `|A| · (|A| - 1) / 2 ≤ M - 1`

which implies `|A| ≤ (1 + √(8M - 7))/2 ∼ √(2M)`.

### The counterexample

The **fragile variant** (`fragile_variant`) demands `(√2 + ε) · √M ≤ |A ∪ B|`. Since `(√2 + ε) · √M` exceeds the counting-bound ceiling `√(2M)` for large `M`, no Sidon set can be this dense. Concretely:

1. Fix any `ε > 0`, obtain the purported threshold `Mε`
2. Choose `N = max(Mε, M₀) + 1` where `M₀` witnesses the counting bound's dominance
3. Take `A = {1}` (a valid Sidon set in `[1, N]`)
4. For any `M ≥ N ≥ M₀`, any Sidon extension `A ∪ B ⊆ [1, M]` satisfies `|A ∪ B| < (√2 + ε)√M`
5. This contradicts the fragile variant's requirement `(√2 + ε)√M ≤ |A ∪ B|`

### What was proved in Lean (in `Main.lean`)

All counterexample-related theorems compile without `sorry` and use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`):

- **`sidon_card_bound`**: The counting bound `|A|(|A|-1)/2 ≤ M-1` for Sidon sets in `[1,M]`
- **`sidon_card_sq_sub_card_le`**: Real-valued corollary `k² - k ≤ 2M - 2`
- **`sidon_eventually_below_sqrt2_plus_eps`**: For any `δ > 0`, ∃ `M₀` s.t. for `M ≥ M₀`, all Sidon sets in `[1,M]` have `< (√2 + δ)√M` elements
- **`singleton_one_sidon`**, **`singleton_one_subset_Icc`**, **`union_subset_Icc`**: Helper lemmas for the witness construction
- **`fragile_variant_false`**: **The main result** — the fragile variant is provably false (`¬ fragile_variant`)

The original `erdos_44_sidon_extension` (with `(1-ε)√M`) remains as `sorry` — it is related to open Erdős Problem 44 and is left as a conjecture.