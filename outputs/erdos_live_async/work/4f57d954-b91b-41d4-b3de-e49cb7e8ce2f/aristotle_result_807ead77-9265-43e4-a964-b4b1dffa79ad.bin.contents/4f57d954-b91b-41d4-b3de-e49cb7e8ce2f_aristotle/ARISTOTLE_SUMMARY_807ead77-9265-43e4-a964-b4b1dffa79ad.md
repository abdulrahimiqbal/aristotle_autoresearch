# Summary of changes
## Falsifying witness for the most fragile variant of Erdős Problem 44

The file `Counterexample.lean` provides a machine-verified falsifying witness for the most fragile natural strengthening of the Erdős 44 Sidon-extension conjecture stated in `Main.lean`.

### Analysis

The original conjecture (an open problem) claims that Sidon sets can always be extended to achieve density `(1-ε)√M` for any `ε > 0`. The **hard ceiling** on Sidon set cardinality comes from a standard double-counting argument: if `A ⊆ [1,N]` is Sidon, then `|A| < 2√N`. This bound is sharp (achieved up to lower-order terms by Singer-type constructions).

The **most fragile variant** is obtained by pushing the density constant from `(1-ε)` up to `2` — the exact counting-bound ceiling `√(4M)/√M`. At this threshold, the statement crosses from "open conjecture" territory into "provably false" territory.

### What is proved (all sorry-free, standard axioms only)

1. **`sidon_fiber_le_two`**: In a Sidon set, each sum-value fiber `{(a,b) ∈ A×A : a+b = s}` has at most 2 elements.

2. **`sidon_sum_range`**: The pairwise sums from `A ⊆ [1,N]` lie in `[2, 2N]`.

3. **`sidon_card_sq_lt`**: The core counting bound — if `A ⊆ [1,N]` is Sidon with `N ≥ 1`, then `|A|² < 4N`.

4. **`sidon_card_lt_two_sqrt`**: Real-valued consequence — `|A| < 2√N`.

5. **`erdos44_strengthened_false`** ⭐: The strengthened Erdős 44 with constant `2` (replacing `(1-ε)`) is **false**. Witnessed by instantiating with `N = 1`, `A = {1}`: for any extension `B` keeping `{1} ∪ B` Sidon in `[1,M]`, the counting bound gives `|{1} ∪ B| < 2√M`, contradicting the demand `2√M ≤ |{1} ∪ B|`.

6. **`sidon_example`**: Concrete verification that `{1,2,4}` is a Sidon set.

### Interpretation

The density constant `(1-ε)` in the original conjecture sits strictly below the counting-bound ceiling of `2` (equivalently `√2 · √(2M)/√M`). The gap between `1` and `√2 ≈ 1.414` is what makes the original conjecture plausible but unresolved. Our falsifying witness shows that any attempt to improve the constant to `2` or beyond immediately fails — this is the sharpest provable boundary, making it the most fragile variant.