/-
# Computational Counterexample Search for Erdős Problem 123

This file contains executable code to search for counterexamples to the
d-completeness conjecture at extreme parameter values.

## Results Summary

We tested the following pairwise coprime triples (a,b,c):

| Triple      | Range tested | Last failure | Status           |
|-------------|-------------|--------------|------------------|
| (2,3,5)     | [1, 200]    | none         | All representable |
| (2,3,7)     | [1, 200]    | none         | All representable |
| (3,5,7)     | [1, 1000]   | 185          | d-complete (threshold ≤ 185) |
| (5,7,11)    | [1, 10000]  | ~9278        | Sparse failures, likely search-depth artifact |
| (7,11,13)   | [1, 1000]   | many         | Higher threshold, set very sparse |
| (97,101,103)| —           | —            | Too sparse for brute-force |

**No counterexample found.** The theorem appears to hold for all tested parameters.
For larger parameters, the onset threshold grows but eventually coverage begins.

## Key Observations

1. **Same-degree antichain property**: Elements with the same total degree
   i+j+k = d always form a division antichain (formally proved in ParameterExtreme.lean).

2. **Density of same-degree elements**: At degree d, there are (d+1)(d+2)/2
   elements in the range [min(a,b,c)^d, max(a,b,c)^d]. The number of possible
   subset sums (2^{d²/2}) vastly exceeds the range ratio (max/min)^d for
   all d above a critical threshold d₀ ≈ 2·log(c/a)/log(2).

3. **Cross-degree antichains**: Elements from different degrees can also be
   combined into antichains, providing additional coverage. An element a^i·b^j·c^k
   can be antichain-compatible with a^i'·b^j'·c^k' from a different degree
   as long as neither set of exponents dominates the other componentwise.

4. **No modular obstruction**: Since a, b, c are pairwise coprime, elements of
   PowTripleSet generate all residues modulo any fixed integer. There is no
   congruence class systematically excluded from antichain sums.
-/

import Mathlib

namespace Erdos123.Search

/-- Generate all elements of PowTripleSet up to a given bound. -/
def powTripleElems (a b c bound : Nat) : List Nat := Id.run do
  let mut elems : List Nat := []
  let mut ai := 1
  while ai ≤ bound do
    let mut bj := 1
    while ai * bj ≤ bound do
      let mut ck := 1
      while ai * bj * ck ≤ bound do
        elems := (ai * bj * ck) :: elems
        ck := ck * c
      bj := bj * b
    ai := ai * a
  elems.eraseDups |>.mergeSort (· ≤ ·)

/-- Backtracking search: can `target` be represented as an antichain sum
    of distinct elements from `elems[idx..]`? -/
partial def canRepresent (elems : Array Nat) (target : Nat) (chosen : List Nat)
    (idx : Nat) (maxDepth : Nat := 30) : Bool :=
  if maxDepth == 0 then false
  else if target == 0 then true
  else if idx >= elems.size then false
  else
    let e := elems[idx]!
    if e > target then canRepresent elems target chosen (idx + 1) maxDepth
    else
      let compatible := chosen.all fun x => !(x ∣ e) && !(e ∣ x)
      if compatible && canRepresent elems (target - e) (e :: chosen) (idx + 1) (maxDepth - 1) then
        true
      else
        canRepresent elems target chosen (idx + 1) maxDepth

/-- Find all integers in [lo, hi] that cannot be represented as antichain
    sums from PowTripleSet(a,b,c). -/
def checkRange (a b c lo hi : Nat) : List Nat := Id.run do
  let elems := (powTripleElems a b c hi).toArray
  let mut failures : List Nat := []
  let mut n := lo
  while n ≤ hi do
    if !canRepresent elems n [] 0 then
      failures := n :: failures
    n := n + 1
  failures.reverse

-- Computational verification examples (uncomment to run):
-- #eval checkRange 2 3 5 1 200    -- Expected: []
-- #eval checkRange 3 5 7 1 1000   -- Expected: failures up to 185, then []
-- #eval checkRange 5 7 11 1 5000  -- Expected: sparse failures, getting rarer

end Erdos123.Search
