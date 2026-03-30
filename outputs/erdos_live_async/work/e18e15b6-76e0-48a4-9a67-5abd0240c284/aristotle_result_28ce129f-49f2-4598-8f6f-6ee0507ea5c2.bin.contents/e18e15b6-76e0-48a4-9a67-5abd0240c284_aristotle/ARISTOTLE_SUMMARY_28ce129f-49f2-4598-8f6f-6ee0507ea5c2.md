# Summary of changes
## Summary

### What was accomplished

The file `Main.lean` contains a formalization of a generalization of **Erdős Problem 123**, asking whether the multiplicative semigroup `{a^i · b^j · c^k}` for pairwise coprime `a, b, c > 1` is d-complete (every sufficiently large integer is an antichain sum from this set).

**Proved lemmas (all sorries filled except the main open conjecture):**

1. **`div_iff_exp_le`** — For pairwise coprime bases, divisibility equals coordinate-wise ≤ on exponent vectors.

2. **`powTripleSet_101_103_107_le_10203`** — Complete enumeration of elements of PowTripleSet(101,103,107) up to 10203.

3. **`no_element_10202_10203`** — No element of the set lies in {10202, 10203}.

4. **`powTripleSet_101_103_107_le_1030303`** — Complete enumeration of elements up to 1030303.

5. **`no_antichain_sum_10203`** — **n = 10203 = 101² + 2 is NOT representable** as an antichain sum from PowTripleSet(101,103,107).

6. **`no_antichain_sum_1030303`** — **n = 1030303 = 101³ + 2 is NOT representable** as an antichain sum from PowTripleSet(101,103,107).

### Counterexample search results

**No full counterexample was found.** The systematic pattern `n = 101^m + 2` produces non-representable numbers for m = 2, 3, 4, ..., up to ~m ≈ 80, but only finitely many — not enough to disprove the "eventually all" claim. For large m (≳80), the total sum of lower-level elements exceeds 101^m, breaking the argument. Dense cases like (2,3,5) showed perfect coverage up to n=100.

### Main theorem

The theorem `erdos_123_d_complete_sequences` remains `sorry`'d. It is a generalization of Erdős Problem 123, a well-known open problem in additive combinatorics. Neither a proof nor a full counterexample exists in the literature.

### Files

- `Main.lean` — All definitions, proved auxiliary lemmas, non-representability theorems, and the sorry'd main conjecture.
- `ANALYSIS.md` — Detailed analysis of the counterexample search, computational evidence, and why the problem remains open.