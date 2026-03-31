# Parameter Extreme Exploration for Erdős Problem 44

## Problem Statement

For all ε > 0, there exists Mε such that for all N ≥ 1 and all Sidon sets A ⊆ [1, N],
there exists M ≥ max(N, Mε) and B ⊆ [N+1, M] with A ∪ B Sidon and
|A ∪ B| ≥ (1 - ε)√M.

## Parameter Extreme: ε → 0⁺

The "parameter extreme" is the case ε → 0, where the required density
approaches √M. At ε = 0, the statement asks for |A ∪ B| ≥ √M exactly.

## Counterexample Search Results

### Approach 1: Greedy Algorithm Testing

We tested greedy Sidon set extensions for various starting sets and M values:

```
Starting set A = [1, 2, 5, 11, 22] (5 elements, Sidon) in [1, 22]:
  M=500:  |A∪B|=21, √M≈22.4, ratio≈0.94
  M=1000: |A∪B|=27, √M≈31.6, ratio≈0.85
  M=2000: |A∪B|=35, √M≈44.7, ratio≈0.78

Starting set A = [1, 3, 7, 12, 20] (5 elements, Sidon) in [1, 20]:
  M=500:  |A∪B|=19, √M≈22.4, ratio≈0.85
  M=1000: |A∪B|=27, √M≈31.6, ratio≈0.85
  M=2000: |A∪B|=35, √M≈44.7, ratio≈0.78
```

**Observation**: The greedy algorithm achieves ratio ≈ 0.78–0.94, declining for
larger M. However, greedy Sidon constructions are known to produce sets of size
~N^{1/3} (not ~√N), so this underperformance is expected and does NOT indicate
a counterexample.

### Approach 2: Algebraic Constructions

Singer's construction gives perfect Sidon sets of size p + 1 in
[0, p² + p] for prime p, achieving ratio → 1 as p → ∞. These are
optimal up to lower-order terms.

For the extension problem: given A ⊆ [1, N], the differences of A
block at most |A|² ≈ N differences for B. In [N+1, M] with M >> N²,
this constraint is negligible, suggesting extensions of size ~√M
are achievable.

### Approach 3: Upper Bound Analysis

The Erdős–Turán bound: any Sidon set S ⊆ [1, M] satisfies
|S| ≤ √M + M^{1/4} + 1. Since this is > √M for all M ≥ 1,
there is no **upper bound obstruction** to achieving |A ∪ B| ≥ √M.

The constraint from A: a Sidon set A of size k creates k(k-1)/2
distinct pairwise differences. Extending with B ⊆ [N+1, M] requires
B's differences to avoid A's differences. With ≤ N forbidden values
out of ~M possible differences, the available space is ~M - N,
supporting Sidon sets of size ~√M.

### Approach 4: Specific ε = 0 Check

For the parameter extreme (ε = 0): |A ∪ B| ≥ √M.
- With A = {N+1}, M = (N+1)², we need |A ∪ B| ≥ N+1, which requires
  finding ~N Sidon elements in [(N+1)+1, (N+1)²]. The interval has
  length ~N², plenty for a Sidon set of size ~N.
- No Sidon set A was found for which extension fails at ALL M values.

## Conclusion

**No counterexample or independence witness was found for the parameter extreme.**

The statement appears consistent with all known bounds and constructions.
The difficulty is not in the bound being too tight, but in formally
constructing the required Sidon extension for arbitrary starting sets.
This requires either:

1. **Probabilistic method**: Random subsets of [N+1, M] with appropriate
   density yield Sidon sets with high probability (Erdős–Rényi type argument).
   Not formalized in Mathlib.

2. **Algebraic constructions**: Singer difference sets from finite geometry.
   Not available in Mathlib in the required form.

3. **Greedy with analysis**: A refined greedy argument with density analysis.
   Requires analytic number theory tools not in Mathlib.

The remaining `sorry` in `erdos_44_case_eps_lt_one` represents this genuine
open problem.
