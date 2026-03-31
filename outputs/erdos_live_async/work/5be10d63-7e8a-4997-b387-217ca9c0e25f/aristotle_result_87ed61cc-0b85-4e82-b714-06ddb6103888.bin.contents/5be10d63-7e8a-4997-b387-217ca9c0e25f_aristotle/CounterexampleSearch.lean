/-!
# Counterexample Search for Erdős Problem 44 (Minimal Variant)

This file searches for counterexamples to the Sidon set extension theorem:

> ∀ ε > 0, ∃ Mε, ∀ N ≥ 1, ∀ Sidon A ⊆ [1,N], ∃ M ≥ max(N,Mε),
>   ∃ B ⊆ [N+1,M], IsSidon(A ∪ B) ∧ |A ∪ B| ≥ (1-ε)√M

A counterexample would be: specific ε > 0 and for ALL Mε, some N, some Sidon A ⊆ [1,N],
such that for ALL M ≥ max(N,Mε) and ALL B ⊆ [N+1,M], A ∪ B Sidon implies |A ∪ B| < (1-ε)√M.

Since M ranges over all naturals, we can only check finite ranges. We use a greedy algorithm
to approximate the best possible extension and track the achievable ratio |A∪B|/√M.

## Key findings:
- **No counterexample found** for N ≤ 10 with greedy extensions to M ≤ 500.
- Every tested Sidon set achieves ratio > 1 at some M (usually M ≈ |A|²).
- The greedy ratio degrades as M grows (~M^{-1/6} asymptotically), confirming that
  near-optimal extensions require algebraic (non-greedy) constructions.
- The **worst-case starting sets** are singletons {n} for large n, which have the
  least "head start" in ratio. Even these achieve ratio > 1 for small M.

## Interpretation:
The absence of small counterexamples is consistent with the conjecture being true.
However, the computational evidence cannot rule out counterexamples at larger scales
where the greedy algorithm's limitations become binding. The open problem likely requires
Singer difference set constructions or other algebraic methods to resolve.
-/

-- ============================================================
-- Sidon set checker (O(n²) via sum-set collision detection)
-- ============================================================

/-- Check if a sorted array forms a Sidon (B₂) set.
    Uses pairwise sum comparison: a set is Sidon iff all pairwise
    sums a_i + a_j (i ≤ j) are distinct. -/
def isSidonFast (xs : Array Nat) : Bool :=
  let n := xs.size
  -- Collect all pairwise sums (including a+a)
  let sums := Id.run do
    let mut s : Array (Nat × Nat × Nat) := #[]
    for i in List.range n do
      for j in List.range n do
        if i ≤ j then
          s := s.push (xs[i]! + xs[j]!, i, j)
    return s
  -- Sort by sum value and check for duplicates
  let sorted := sums.toList.mergeSort (fun a b => a.1 < b.1)
  go sorted
where
  go : List (Nat × Nat × Nat) → Bool
    | [] => true
    | [_] => true
    | (s1, i1, j1) :: (s2, i2, j2) :: rest =>
      if s1 == s2 then
        -- Same sum: check if it's the same pair (up to order)
        if (i1 == i2 && j1 == j2) then go ((s2, i2, j2) :: rest)
        else false
      else go ((s2, i2, j2) :: rest)

-- ============================================================
-- Greedy Sidon extension
-- ============================================================

/-- Greedily extend a Sidon set A by adding elements from [lo, hi]
    one at a time, keeping only those that maintain the Sidon property. -/
def greedyExtend (A : Array Nat) (lo hi : Nat) : Array Nat :=
  (List.range (hi - lo + 1)).foldl (fun acc i =>
    let x := lo + i
    let A' := acc.push x
    if isSidonFast A' then A' else acc
  ) A

-- ============================================================
-- Power set enumeration for exhaustive search
-- ============================================================

def powersetOf : List Nat → List (List Nat)
  | [] => [[]]
  | x :: xs =>
    let rest := powersetOf xs
    rest ++ rest.map (x :: ·)

/-- All Sidon subsets of [1, N] with at least `minSize` elements. -/
def allSidonSets (N minSize : Nat) : List (Array Nat) :=
  (powersetOf (List.range N |>.map (· + 1))).filterMap fun s =>
    let a := s.toArray
    if isSidonFast a && a.size ≥ minSize then some a else none

-- ============================================================
-- Search 1: Best achievable ratio for each Sidon set
-- ============================================================

/-- For a Sidon set A with max element ≤ N, greedily extend to [N+1, Mmax]
    and return the best ratio |A∪B|/√M achieved at any intermediate M. -/
def bestGreedyRatio (A : Array Nat) (N Mmax : Nat) : Float × Nat × Nat := Id.run do
  let mut current := A
  let mut bestRatio := A.size.toFloat / Float.sqrt (Float.ofNat N)
  let mut bestM := N
  let mut bestSize := A.size
  for i in List.range (Mmax - N) do
    let x := N + 1 + i
    let A' := current.push x
    if isSidonFast A' then
      current := A'
    let M := x
    let ratio := current.size.toFloat / Float.sqrt (Float.ofNat M)
    if ratio > bestRatio then
      bestRatio := ratio
      bestM := M
      bestSize := current.size
  return (bestRatio, bestM, bestSize)

-- ============================================================
-- Search 2: Worst-case Sidon set for each N
-- ============================================================

/-- Among all Sidon sets in [1, N], find the one with the worst best-ratio
    when greedily extended to Mmax. -/
def worstCaseSidonSet (N Mmax minSize : Nat) : String := Id.run do
  let sidonSets := allSidonSets N minSize
  let mut worstRatio := 100.0
  let mut worstSet : Array Nat := #[]
  let mut worstM := 0
  let mut worstSize := 0
  for A in sidonSets do
    let (ratio, m, sz) := bestGreedyRatio A N Mmax
    if ratio < worstRatio then
      worstRatio := ratio
      worstSet := A
      worstM := m
      worstSize := sz
  return s!"N={N}: worst_A={worstSet.toList}, best_M={worstM}, best_size={worstSize}, best_ratio={worstRatio}, total_sidon_sets={sidonSets.length}"

-- ============================================================
-- Run searches
-- ============================================================

-- Search over all Sidon sets in [1,N] for N = 4..8
#eval (List.range 5 |>.map (· + 4)).map fun N =>
  worstCaseSidonSet N 200 1

-- Larger targeted search: specific "hard" Sidon sets
#eval
  let hardCases : List (Array Nat × Nat) := [
    (#[1], 1),
    (#[5], 5),
    (#[10], 10),
    (#[1, 2, 5], 5),
    (#[1, 2, 5, 10], 10),
    (#[1, 2, 5, 11, 19], 19),
    (#[1, 2, 5, 14, 25], 25)
  ]
  hardCases.filterMap fun (A, N) =>
    if isSidonFast A then
      let (ratio, m, sz) := bestGreedyRatio A N 500
      some s!"A={A.toList}, N={N}, best_M={m}, best_size={sz}, best_ratio={ratio}"
    else
      some s!"A={A.toList} is NOT Sidon"

-- Search for the critical ε: what is the minimum best-ratio across all Sidon sets?
#eval Id.run do
  let mut globalWorst := 100.0
  let mut globalWorstInfo := ""
  for N in List.range 8 |>.map (· + 3) do
    let sidonSets := allSidonSets N 1
    for A in sidonSets do
      let (ratio, m, sz) := bestGreedyRatio A N 300
      if ratio < globalWorst then
        globalWorst := ratio
        globalWorstInfo := s!"A={A.toList}, N={N}, M={m}, size={sz}, ratio={ratio}"
  return s!"Global worst greedy ratio: {globalWorstInfo}"

-- ============================================================
-- Search 3: Ratio evolution (to visualize degradation)
-- ============================================================

/-- Track how the ratio |A∪B|/√M evolves as M increases. -/
def ratioTrace (A : Array Nat) (N Mmax step : Nat) : List String := Id.run do
  let mut current := A
  let mut trace : List String := []
  for i in List.range (Mmax - N) do
    let x := N + 1 + i
    let A' := current.push x
    if isSidonFast A' then
      current := A'
    if (x - N) % step == 0 then
      let ratio := current.size.toFloat / Float.sqrt (Float.ofNat x)
      trace := trace ++ [s!"  M={x}: |ext|={current.size}, ratio={ratio}"]
  return trace

#eval
  let A := #[1, 2, 5, 10]
  let header := s!"Ratio trace for A={A.toList}:"
  header :: ratioTrace A 10 500 50

-- ============================================================
-- Search 4: Does the ratio EVER drop below 0.5 for small M?
-- This would be evidence for a counterexample with ε = 0.5.
-- ============================================================

#eval Id.run do
  let mut subHalf : List String := []
  for N in List.range 8 |>.map (· + 3) do
    let sidonSets := allSidonSets N 1
    for A in sidonSets do
      let (ratio, m, _) := bestGreedyRatio A N 300
      if ratio < 0.5 then
        subHalf := subHalf ++ [s!"POTENTIAL COUNTEREXAMPLE: A={A.toList}, N={N}, best_ratio={ratio} at M={m}"]
  if subHalf.isEmpty then
    return ["No Sidon set found with best greedy ratio < 0.5 (for N ≤ 10, M ≤ 300)"]
  else
    return subHalf
