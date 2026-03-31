# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 9
- Succeeded: 0
- Stalled: 7
- Failed: 0
- Pending: 2

## Campaign Health

- active=2 pending=2 running=1 completed=7 failed=0
- structured ingestion success rate: 1.0
- semantic reuse rate: 0.131
- transfer usage rate: 0.286
- reusable structure rate: 0.429
- obstruction discovery rate: 0.714
- high-priority frontier share: 0.636
- repeated no-signal streak: 0
- duplicate frontier pressure: 1
- move-family diversity: frontier=9 completed=5
- open incidents: 4

## Version Drift

- `manifest_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `prompt_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `move_registry_version` historical=`2026.03.phase4` current=`2026.03.phase7` count=26
- `runtime_policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26

## Discovery Graph

- nodes: 92
- edges: 104
- verified-like nodes: 53
- `experiment` `9941d619-a8ab-4ac9-ab9c-1503088b4e65` confidence=1.0 provenance=execution
- `experiment` `ddb1aae2-1b93-438c-9165-39a34b6f05c6` confidence=1.0 provenance=execution
- `experiment` `bff4c05f-d103-47ac-83f8-1164972a1bca` confidence=1.0 provenance=execution
- `experiment` `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` confidence=1.0 provenance=execution
- `experiment` `456ae293-4a69-4679-b093-913c49b3b304` confidence=1.0 provenance=execution
- `experiment` `e7ffb40d-1e42-444e-8ffd-4d486f55a51e` confidence=1.0 provenance=execution
- `experiment` `b1167253-8940-4176-b5b6-fc4968f3735f` confidence=1.0 provenance=execution
- `verified_lemma` `PowTripleSet : (a b c : ℕ) : Set ℕ` confidence=0.95 provenance=artifact
- `verified_lemma` `PairwiseCoprime3 : (a b c : ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `IsDivisionAntichain : (s : Finset ℕ) : Prop` confidence=0.95 provenance=artifact

## Discovery Questions

- No open discovery questions.

## Conjecture Tuning

### Erdos Problem 123: d-complete triple-power antichain sums

- seed question [boundary_case]: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- seed question [bridge_lemma]: Which reusable covering or divisibility-extraction lemmas recur across special parameter triples and look strong enough to promote?
- seed question [transfer]: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- focus areas: d-completeness boundary cases, special parameter triples, reusable covering lemmas, antichain and divisibility extraction lemmas, obstruction patterns and counterexamples, bridge lemmas from solved motifs, transfer-worthy motifs
- preferred move families: invariant_mining, extremal_case, decompose_subclaim, equivalent_view, witness_minimization, adversarial_counterexample, transfer_reformulation

## Active jobs

- `IN_PROGRESS`: 1
- `QUEUED`: 1

## Recently completed

- `b1167253-8940-4176-b5b6-fc4968f3735f` on `erdos-123` -> `stalled`
- `e7ffb40d-1e42-444e-8ffd-4d486f55a51e` on `erdos-123` -> `stalled`
- `456ae293-4a69-4679-b093-913c49b3b304` on `erdos-123` -> `stalled`
- `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` on `erdos-123` -> `stalled`
- `bff4c05f-d103-47ac-83f8-1164972a1bca` on `erdos-123` -> `stalled`

## Recurring lemmas

- `IsDComplete : (A : Set ℕ) : Prop` — reuse=10
- `IsDivisionAntichain : (s : Finset ℕ) : Prop` — reuse=10
- `PairwiseCoprime3 : (a b c : ℕ) : Prop` — reuse=10
- `PowTripleSet : (a b c : ℕ) : Set ℕ` — reuse=10
- `one_mem_PowTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c` — reuse=4
- `promoted_lemma : True` — reuse=4
- `IsDCompleteAll : (A : Set ℕ) : Prop` — reuse=2
- `IsDComplete_mono [sorry at line 215]: the foundation for any future formal proof.

The sorry here represents the core open mathematical content, not a gap in
the formalization infrastructure. -/` — reuse=2
- `IsDComplete_with_antichain : (A : Set ℕ) : Prop` — reuse=2
- `PowTripleSet_mul_closed : {a b c : ℕ} {m n : ℕ}` — reuse=2
- `PowTripleSet_pos : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `PowTripleSet_pos : {a b c n : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)` — reuse=2
- `a_mem_PowTripleSet : (a b c : ℕ) : a ∈ PowTripleSet a b c` — reuse=2
- `anonymous_have : = Nat.dvd_gcd (dvd_refl _) h` — reuse=2
- `anonymous_have : = coprime_pow_triple_incomparable ha hb hc hco hne hdiv` — reuse=2
- `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h; aesop;` — reuse=2
- `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h_div.1; have` — reuse=2
- `antichain_of_incomparable_exponents : {a b c : ℕ}` — reuse=2
- `antichain_sum_pow2 : (s : Finset ℕ)` — reuse=2
- `b_mem_PowTripleSet : (a b c : ℕ) : b ∈ PowTripleSet a b c` — reuse=2
- `bridge_interval_coverage : True` — reuse=2
- `brown_completeness_criterion : (f : ℕ → ℕ) (hf0 : f 0 = 1)` — reuse=2
- `c_mem_PowTripleSet : (a b c : ℕ) : c ∈ PowTripleSet a b c` — reuse=2
- `coprime_pow_triple_incomparable : {a b c : ℕ}` — reuse=2
- `cross_family_incomparable : {a b c : ℕ}` — reuse=2
- `diagonal_antichain : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `dvd_iff_exponents_le : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 148]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 204]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 221]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 268]: exact powTripleSet_2bc_dComplete a b
  -- All of a, b, c ≥ 3: requires density of smooth numbers (the blocker)
  sorry` — reuse=2
- `erdos_123_modified_false : :` — reuse=2
- `erdos_123_no_coprimality_false [sorry at line 200]: --       PairwiseCoprime3 a b c →
--       IsDComplete (PowTripleSet a b c) := by
--   sorry` — reuse=2
- `exists_close_pair [sorry at line 222]: (hab : Nat.Coprime a b) :
    ∃ p q : ℕ, 0 < p ∧ b ^ q < a ^ p ∧ a ^ p ≤ 2 * b ^ q := by
  sorry

/-- For coprime a, b ≥ 2, the multiplicative semigroup {a^i · b^j : i,j ∈ ℕ}` — reuse=2
- `exponent_map_injective : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `h_binary : ∃ s : Finset ℕ, (∑ i ∈ s, 2 ^ i) = n` — reuse=2
- `h_card_eq_one : s.card = 1` — reuse=2
- `h_card_le_one : s.card ≤ 1` — reuse=2
- `h_contra : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂` — reuse=2
- `h_diff : m - f (k + 1) ≤ ∑ i ∈ Finset.range (k + 1), f i` — reuse=2
- `h_div : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ ∧ a ^ i₂ * b ^ j₂ * c ^ k₂ ∣ a ^ i₁ * b ^ j₁ * c ^ k₁` — reuse=2
- `h_div : i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ ∧ i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁` — reuse=2
- `h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂` — reuse=2
- `h_div_c : c ^ (k₁ - k₂) ∣ a ^ i₂ * b ^ j₂` — reuse=2
- `h_div_one : c ^ (k₁ - k₂) ∣ 1` — reuse=2
- `h_exp : a ^ q = b ^ p` — reuse=2
- `h_factor_a : a ^ i₁ ∣ a ^ i₂` — reuse=2
- `h_factor_b : b ^ j₁ ∣ b ^ j₂` — reuse=2
- `h_factor_c : c ^ k₁ ∣ c ^ k₂` — reuse=2
- `h_ge_3 : ∀ y ∈ s, y ≥ 3` — reuse=2
- `hcop : Nat.Coprime (a ^ (i₁ - i₂)) (b ^ j₂ * c ^ k₂)` — reuse=2
- `hs_powers_of_two : ∀ x ∈ s, ∃ m : ℕ, x = 2 ^ m` — reuse=2
- `hs_sum_powers_of_two : ∃ m : ℕ, s.sum id = 2 ^ m` — reuse=2
- `irrational_log_ratio : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)` — reuse=2
- `isDComplete_mono : {A B : Set ℕ} (hAB : A ⊆ B) (hA : IsDComplete A) :` — reuse=2
- `isDComplete_of_antichain : {A : Set ℕ} (h : IsDComplete_with_antichain A) :` — reuse=2
- `mul_mem_powTripleSet : {a b c m n : ℕ}` — reuse=2
- `no_antichain_sum_two : (s : Finset ℕ) (hsub : (↑s : Set ℕ) ⊆ PowTripleSet 3 5 7)` — reuse=2
- `not_eventually_pow2 : :` — reuse=2
- `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :` — reuse=2
- `pow2_antichain_card_le_one : (s : Finset ℕ)` — reuse=2
- `powPair_eventually_dense [sorry at line 235]: ∃ N₀ : ℕ, ∀ M : ℕ, N₀ ≤ M →
      ∃ i j : ℕ, M < a ^ i * b ^ j ∧ a ^ i * b ^ j ≤ 2 * M := by
  sorry

-- ============================================================` — reuse=2
- `powTripleSet_222_eq : : PowTripleSet 2 2 2 = {n | ∃ m : ℕ, n = 2 ^ m}` — reuse=2
- `powTripleSet_222_not_dComplete : :` — reuse=2
- `powTripleSet_2bc_dComplete : (b c : ℕ) :` — reuse=2
- `powTripleSet_357_ge_three : {n : ℕ} (hn : n ∈ PowTripleSet 3 5 7) (hn2 : n ≥ 2) :` — reuse=2
- `powTripleSet_357_no_two : : 2 ∉ PowTripleSet 3 5 7` — reuse=2
- `powTripleSet_swap12 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet b a c` — reuse=2
- `powTripleSet_swap23 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet a c b` — reuse=2
- `pow_a_mem : (a b c : ℕ) (i : ℕ) : a ^ i ∈ PowTripleSet a b c` — reuse=2
- `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :` — reuse=2
- `pow_b_mem : (a b c : ℕ) (j : ℕ) : b ^ j ∈ PowTripleSet a b c` — reuse=2
- `pow_b_mem : {a b c : ℕ} (ha : 0 < a) (hc : 0 < c) (j : ℕ) :` — reuse=2
- `pow_c_mem : (a b c : ℕ) (k : ℕ) : c ^ k ∈ PowTripleSet a b c` — reuse=2
- `pow_c_mem : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (k : ℕ) :` — reuse=2
- `pow_ne_pow_of_coprime : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)` — reuse=2
- `product_mem : {a b c : ℕ} (i j k : ℕ) :` — reuse=2

## Space Search Progress

- recurring lemmas: 77 clusters
- recurring subgoals: 1 clusters
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- recurring lemmas are beginning to cluster across runs
- repeated subgoal `erdos_123_d_complete_sequences: pairwisecoprime3 v v v → isdcomplete (powtripleset v v v) := by sorry` across 3 runs
- no blocker patterns aggregated yet
- move `perturb_assumption` repeatedly yields blocker `unknown` / `partial` (3 runs)
- move `promote_lemma` repeatedly yields blocker `unknown` / `partial` (3 runs)

## Assumption sensitivity

- `a, b, c are pairwise coprime` — avg_sensitivity=0.2 across 1 observations
- `no chosen summand divides another` — avg_sensitivity=0.2 across 1 observations
- `the representation is required only for sufficiently large integers` — avg_sensitivity=0.2 across 1 observations

## Experiment log

### bff4c05f-d103-47ac-83f8-1164972a1bca

- move: `underspecify`
- move family: `legacy.underspecify`
- theorem family: `erdos_problem`
- phase: `mapping`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `72d3ca62-8ac6-4088-9d37-1d9f45d71fa4`
- external status: `COMPLETE`
- objective: Fill in all sorries. Strip imports to expose hidden dependencies. Report intermediate lemmas or unresolved goals. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Minimal context is the safest first pass for exposing missing structure.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; proved=15; generated=9; subgoals=1
- new signal count: 37
- reused signal count: 0
- generated lemmas:
  - `h_factor_a : a ^ i₁ ∣ a ^ i₂`
  - `h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `h_factor_b : b ^ j₁ ∣ b ^ j₂`
  - `h_factor_c : c ^ k₁ ∣ c ^ k₂`
  - `h_div : i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ ∧ i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁`
  - `h_div : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ ∧ a ^ i₂ * b ^ j₂ * c ^ k₂ ∣ a ^ i₁ * b ^ j₁ * c ^ k₁`
  - `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h_div.1; have`
  - `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h; aesop;`
  - `erdos_123_d_complete_sequences [sorry at line 204]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proved lemmas:
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :`
  - `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :`
  - `pow_b_mem : {a b c : ℕ} (ha : 0 < a) (hc : 0 < c) (j : ℕ) :`
  - `pow_c_mem : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (k : ℕ) :`
  - `dvd_iff_exponents_le : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `PowTripleSet_pos : {a b c n : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)`
  - `antichain_of_incomparable_exponents : {a b c : ℕ}`
  - `exponent_map_injective : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `PowTripleSet_mul_closed : {a b c : ℕ} {m n : ℕ}`
  - `product_mem : {a b c : ℕ} (i j k : ℕ) :`
  - `cross_family_incomparable : {a b c : ℕ}`
- candidate lemmas:
  - `h_factor_a : a ^ i₁ ∣ a ^ i₂`
  - `h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `h_factor_b : b ^ j₁ ∣ b ^ j₂`
  - `h_factor_c : c ^ k₁ ∣ c ^ k₂`
  - `h_div : i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ ∧ i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁`
  - `h_div : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ ∧ a ^ i₂ * b ^ j₂ * c ^ k₂ ∣ a ^ i₁ * b ^ j₁ * c ^ k₁`
  - `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h_div.1; have`
  - `anonymous_have : = dvd_iff_exponents_le ha hb hc hab hac hbc |>.1 h; aesop;`
  - `erdos_123_d_complete_sequences [sorry at line 204]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :`
  - `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :`
  - `pow_b_mem : {a b c : ℕ} (ha : 0 < a) (hc : 0 < c) (j : ℕ) :`
  - `pow_c_mem : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (k : ℕ) :`
  - `dvd_iff_exponents_le : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `PowTripleSet_pos : {a b c n : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)`
  - `antichain_of_incomparable_exponents : {a b c : ℕ}`
  - `exponent_map_injective : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `PowTripleSet_mul_closed : {a b c : ℕ} {m n : ℕ}`
  - `product_mem : {a b c : ℕ} (i j k : ℕ) :`
  - `cross_family_incomparable : {a b c : ℕ}`
- unresolved goals:
  - `erdos_123_d_complete_sequences:       PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proof traces:
  - `have h_factor_a : a ^ i₁ ∣ a ^ i₂`
  - `have h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `have h_factor_b : b ^ j₁ ∣ b ^ j₂`
  - `have h_factor_c : c ^ k₁ ∣ c ^ k₂`
  - `have h_div : i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ ∧ i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt` (8751 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin` (8948 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/ANALYSIS.md` (8645 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/ARISTOTLE_SUMMARY_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.md` (2861 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/AristotleWorkspace.lean` (10837 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/Main.lean` (26 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/lakefile.toml` (206 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/ANALYSIS.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/AristotleWorkspace.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/README.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/bff4c05f-d103-47ac-83f8-1164972a1bca/aristotle_result_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.bin.contents/bff4c05f-d103-47ac-83f8-1164972a1bca_aristotle/ARISTOTLE_SUMMARY_72d3ca62-8ac6-4088-9d37-1d9f45d71fa4.md`
- evaluation total: 243.4
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21

- move: `promote_lemma`
- move family: `invariant_mining`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `67636ee5-eb7b-461b-9fcd-0f9d100ddba0`
- external status: `COMPLETE`
- objective: Fill in all sorries. Mine a reusable invariant or monotonicity principle that explains the recurring signal 'unknown'. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring semantic signal 'unknown' suggests a hidden invariant worth isolating.
- campaign priority: 1.75
- transfer score: 0.3125
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; proved=11; generated=8; subgoals=2
- new signal count: 28
- reused signal count: 5
- generated lemmas:
  - `hcop : Nat.Coprime (a ^ (i₁ - i₂)) (b ^ j₂ * c ^ k₂)`
  - `anonymous_have : = Nat.dvd_gcd (dvd_refl _) h`
  - `h_contra : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `h_div_c : c ^ (k₁ - k₂) ∣ a ^ i₂ * b ^ j₂`
  - `h_div_one : c ^ (k₁ - k₂) ∣ 1`
  - `anonymous_have : = coprime_pow_triple_incomparable ha hb hc hco hne hdiv`
  - `IsDComplete_mono [sorry at line 215]: the foundation for any future formal proof.

The sorry here represents the core open mathematical content, not a gap in
the formalization infrastructure. -/`
  - `erdos_123_d_complete_sequences [sorry at line 221]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proved lemmas:
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `PowTripleSet_pos : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `one_mem_PowTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c`
  - `a_mem_PowTripleSet : (a b c : ℕ) : a ∈ PowTripleSet a b c`
  - `b_mem_PowTripleSet : (a b c : ℕ) : b ∈ PowTripleSet a b c`
  - `c_mem_PowTripleSet : (a b c : ℕ) : c ∈ PowTripleSet a b c`
  - `coprime_pow_triple_incomparable : {a b c : ℕ}`
  - `diagonal_antichain : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
- candidate lemmas:
  - `hcop : Nat.Coprime (a ^ (i₁ - i₂)) (b ^ j₂ * c ^ k₂)`
  - `anonymous_have : = Nat.dvd_gcd (dvd_refl _) h`
  - `h_contra : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `h_div_c : c ^ (k₁ - k₂) ∣ a ^ i₂ * b ^ j₂`
  - `h_div_one : c ^ (k₁ - k₂) ∣ 1`
  - `anonymous_have : = coprime_pow_triple_incomparable ha hb hc hco hne hdiv`
  - `IsDComplete_mono [sorry at line 215]: the foundation for any future formal proof.

The sorry here represents the core open mathematical content, not a gap in
the formalization infrastructure. -/`
  - `erdos_123_d_complete_sequences [sorry at line 221]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `PowTripleSet_pos : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
  - `one_mem_PowTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c`
  - `a_mem_PowTripleSet : (a b c : ℕ) : a ∈ PowTripleSet a b c`
  - `b_mem_PowTripleSet : (a b c : ℕ) : b ∈ PowTripleSet a b c`
  - `c_mem_PowTripleSet : (a b c : ℕ) : c ∈ PowTripleSet a b c`
  - `coprime_pow_triple_incomparable : {a b c : ℕ}`
  - `diagonal_antichain : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)`
- unresolved goals:
  - `IsDComplete_mono: the foundation for any future formal proof.

The sorry here represents the core open mathematical co`
  - `erdos_123_d_complete_sequences:       PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proof traces:
  - `have hcop : Nat.Coprime (a ^ (i₁ - i₂)) (b ^ j₂ * c ^ k₂)`
  - `have anonymous_have : = Nat.dvd_gcd (dvd_refl _) h`
  - `have h_contra : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂`
  - `have h_div_c : c ^ (k₁ - k₂) ∣ a ^ i₂ * b ^ j₂`
  - `have h_div_one : c ^ (k₁ - k₂) ∣ 1`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt` (8751 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin` (5981 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/ARISTOTLE_SUMMARY_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.md` (2838 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/AristotleWorkspace.lean` (31 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/AristotleWorkspace/Main.lean` (10833 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lakefile.toml` (189 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lean-toolchain` (25 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/ARISTOTLE_SUMMARY_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/AristotleWorkspace.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/README.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21/aristotle_result_67636ee5-eb7b-461b-9fcd-0f9d100ddba0.bin.contents/b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21_aristotle/AristotleWorkspace/Main.lean`
- evaluation total: 195.82
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### 9941d619-a8ab-4ac9-ab9c-1503088b4e65

- move: `promote_lemma`
- move family: `decompose_subclaim`
- theorem family: `erdos_problem`
- phase: `excavation`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `51be99fa-6b9b-4c6c-9df5-898433246f61`
- external status: `COMPLETE`
- objective: Fill in all sorries. Split the current theorem into a bridge lemma and a remaining reduction built around the recurring subgoal. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Campaign seed 'derive a covering lemma that upgrades interval coverage to eventual d-completeness' is an explicitly requested bridge lemma target.
- campaign priority: 1.7
- transfer score: 0.3
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; generated=2
- new signal count: 2
- reused signal count: 0
- generated lemmas:
  - `bridge_interval_coverage : True`
  - `promoted_lemma : True`
- candidate lemmas:
  - `bridge_interval_coverage : True`
  - `promoted_lemma : True`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt` (8776 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin` (2859 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/ARISTOTLE_SUMMARY_51be99fa-6b9b-4c6c-9df5-898433246f61.md` (1762 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/Main.lean` (2007 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lakefile.toml` (152 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lean-toolchain` (25 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stderr.txt` (247 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/ARISTOTLE_SUMMARY_51be99fa-6b9b-4c6c-9df5-898433246f61.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/9941d619-a8ab-4ac9-ab9c-1503088b4e65/aristotle_result_51be99fa-6b9b-4c6c-9df5-898433246f61.bin.contents/9941d619-a8ab-4ac9-ab9c-1503088b4e65_aristotle/README.md`
- evaluation total: 13.74
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### ddb1aae2-1b93-438c-9165-39a34b6f05c6

- move: `promote_lemma`
- move family: `legacy.promote_lemma`
- theorem family: `erdos_problem`
- phase: `stress_testing`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `111c2eb8-0247-4974-8ea6-64a151b5af34`
- external status: `COMPLETE`
- objective: Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem. Discovery question: Which d-completeness boundary cases fail because interval-style coverage cannot be upgraded to a divisibility antichain, and what is the sharpest witness?
- rationale: Recurring lemma 'bridge_interval_coverage : True' crossed the promotion threshold.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; generated=1
- new signal count: 0
- reused signal count: 1
- generated lemmas:
  - `promoted_lemma : True`
- candidate lemmas:
  - `promoted_lemma : True`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt` (8756 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin` (2532 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/ARISTOTLE_SUMMARY_111c2eb8-0247-4974-8ea6-64a151b5af34.md` (2170 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/AristotleWorkspace.lean` (332 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/Main.lean` (332 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lakefile.toml` (206 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lean-toolchain` (25 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/ARISTOTLE_SUMMARY_111c2eb8-0247-4974-8ea6-64a151b5af34.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/AristotleWorkspace.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/ddb1aae2-1b93-438c-9165-39a34b6f05c6/aristotle_result_111c2eb8-0247-4974-8ea6-64a151b5af34.bin.contents/ddb1aae2-1b93-438c-9165-39a34b6f05c6_aristotle/README.md`
- evaluation total: 4.75
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### 456ae293-4a69-4679-b093-913c49b3b304

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `stress_testing`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `593ad586-0a26-4254-b2e9-72a6920b2438`
- external status: `COMPLETE`
- objective: Fill in all sorries. The assumption 'a, b, c are pairwise coprime' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'a, b, c are pairwise coprime' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; proved=9; generated=5; subgoals=1
- new signal count: 22
- reused signal count: 4
- generated lemmas:
  - `h_card_le_one : s.card ≤ 1`
  - `h_card_eq_one : s.card = 1`
  - `hs_powers_of_two : ∀ x ∈ s, ∃ m : ℕ, x = 2 ^ m`
  - `hs_sum_powers_of_two : ∃ m : ℕ, s.sum id = 2 ^ m`
  - `erdos_123_no_coprimality_false [sorry at line 200]: --       PairwiseCoprime3 a b c →
--       IsDComplete (PowTripleSet a b c) := by
--   sorry`
- proved lemmas:
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `powTripleSet_222_eq : : PowTripleSet 2 2 2 = {n | ∃ m : ℕ, n = 2 ^ m}`
  - `pow2_antichain_card_le_one : (s : Finset ℕ)`
  - `antichain_sum_pow2 : (s : Finset ℕ)`
  - `not_eventually_pow2 : :`
  - `powTripleSet_222_not_dComplete : :`
- candidate lemmas:
  - `h_card_le_one : s.card ≤ 1`
  - `h_card_eq_one : s.card = 1`
  - `hs_powers_of_two : ∀ x ∈ s, ∃ m : ℕ, x = 2 ^ m`
  - `hs_sum_powers_of_two : ∃ m : ℕ, s.sum id = 2 ^ m`
  - `erdos_123_no_coprimality_false [sorry at line 200]: --       PairwiseCoprime3 a b c →
--       IsDComplete (PowTripleSet a b c) := by
--   sorry`
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `powTripleSet_222_eq : : PowTripleSet 2 2 2 = {n | ∃ m : ℕ, n = 2 ^ m}`
  - `pow2_antichain_card_le_one : (s : Finset ℕ)`
  - `antichain_sum_pow2 : (s : Finset ℕ)`
  - `not_eventually_pow2 : :`
  - `powTripleSet_222_not_dComplete : :`
- unresolved goals:
  - `erdos_123_no_coprimality_false: --       PairwiseCoprime3 a b c →
--       IsDComplete (PowTripleSet a b c) := by
--   sorry`
- proof traces:
  - `have h_card_le_one : s.card ≤ 1`
  - `have h_card_eq_one : s.card = 1`
  - `have hs_powers_of_two : ∀ x ∈ s, ∃ m : ℕ, x = 2 ^ m`
  - `have hs_sum_powers_of_two : ∃ m : ℕ, s.sum id = 2 ^ m`
  - `depends_on: ly (in IsDComplete)`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stdout.txt` (8761 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin` (6135 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/ARISTOTLE_SUMMARY_593ad586-0a26-4254-b2e9-72a6920b2438.md` (2501 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/Main.lean` (10324 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lakefile.toml` (178 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lean-toolchain` (25 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_stderr.txt` (247 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/ARISTOTLE_SUMMARY_593ad586-0a26-4254-b2e9-72a6920b2438.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_result_593ad586-0a26-4254-b2e9-72a6920b2438.bin.contents/456ae293-4a69-4679-b093-913c49b3b304_aristotle/README.md`
- evaluation total: 154.167
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### e7ffb40d-1e42-444e-8ffd-4d486f55a51e

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `a554206b-b500-4e66-8e51-469b5ef6a2f1`
- external status: `COMPLETE`
- objective: Fill in all sorries. The assumption 'no chosen summand divides another' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'no chosen summand divides another' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; proved=18; generated=6; subgoals=4
- new signal count: 33
- reused signal count: 5
- generated lemmas:
  - `h_diff : m - f (k + 1) ≤ ∑ i ∈ Finset.range (k + 1), f i`
  - `h_binary : ∃ s : Finset ℕ, (∑ i ∈ s, 2 ^ i) = n`
  - `h_exp : a ^ q = b ^ p`
  - `exists_close_pair [sorry at line 222]: (hab : Nat.Coprime a b) :
    ∃ p q : ℕ, 0 < p ∧ b ^ q < a ^ p ∧ a ^ p ≤ 2 * b ^ q := by
  sorry

/-- For coprime a, b ≥ 2, the multiplicative semigroup {a^i · b^j : i,j ∈ ℕ}`
  - `powPair_eventually_dense [sorry at line 235]: ∃ N₀ : ℕ, ∀ M : ℕ, N₀ ≤ M →
      ∃ i j : ℕ, M < a ^ i * b ^ j ∧ a ^ i * b ^ j ≤ 2 * M := by
  sorry

-- ============================================================`
  - `erdos_123_d_complete_sequences [sorry at line 268]: exact powTripleSet_2bc_dComplete a b
  -- All of a, b, c ≥ 3: requires density of smooth numbers (the blocker)
  sorry`
- proved lemmas:
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete_with_antichain : (A : Set ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `isDComplete_of_antichain : {A : Set ℕ} (h : IsDComplete_with_antichain A) :`
  - `isDComplete_mono : {A B : Set ℕ} (hAB : A ⊆ B) (hA : IsDComplete A) :`
  - `one_mem_powTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c`
  - `pow_a_mem : (a b c : ℕ) (i : ℕ) : a ^ i ∈ PowTripleSet a b c`
  - `pow_b_mem : (a b c : ℕ) (j : ℕ) : b ^ j ∈ PowTripleSet a b c`
  - `pow_c_mem : (a b c : ℕ) (k : ℕ) : c ^ k ∈ PowTripleSet a b c`
  - `mul_mem_powTripleSet : {a b c m n : ℕ}`
  - `powTripleSet_swap12 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet b a c`
  - `powTripleSet_swap23 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet a c b`
  - `brown_completeness_criterion : (f : ℕ → ℕ) (hf0 : f 0 = 1)`
  - `powTripleSet_2bc_dComplete : (b c : ℕ) :`
  - `pow_ne_pow_of_coprime : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)`
  - `irrational_log_ratio : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)`
- candidate lemmas:
  - `h_diff : m - f (k + 1) ≤ ∑ i ∈ Finset.range (k + 1), f i`
  - `h_binary : ∃ s : Finset ℕ, (∑ i ∈ s, 2 ^ i) = n`
  - `h_exp : a ^ q = b ^ p`
  - `exists_close_pair [sorry at line 222]: (hab : Nat.Coprime a b) :
    ∃ p q : ℕ, 0 < p ∧ b ^ q < a ^ p ∧ a ^ p ≤ 2 * b ^ q := by
  sorry

/-- For coprime a, b ≥ 2, the multiplicative semigroup {a^i · b^j : i,j ∈ ℕ}`
  - `powPair_eventually_dense [sorry at line 235]: ∃ N₀ : ℕ, ∀ M : ℕ, N₀ ≤ M →
      ∃ i j : ℕ, M < a ^ i * b ^ j ∧ a ^ i * b ^ j ≤ 2 * M := by
  sorry

-- ============================================================`
  - `erdos_123_d_complete_sequences [sorry at line 268]: exact powTripleSet_2bc_dComplete a b
  -- All of a, b, c ≥ 3: requires density of smooth numbers (the blocker)
  sorry`
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete_with_antichain : (A : Set ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `isDComplete_of_antichain : {A : Set ℕ} (h : IsDComplete_with_antichain A) :`
  - `isDComplete_mono : {A B : Set ℕ} (hAB : A ⊆ B) (hA : IsDComplete A) :`
  - `one_mem_powTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c`
  - `pow_a_mem : (a b c : ℕ) (i : ℕ) : a ^ i ∈ PowTripleSet a b c`
  - `pow_b_mem : (a b c : ℕ) (j : ℕ) : b ^ j ∈ PowTripleSet a b c`
  - `pow_c_mem : (a b c : ℕ) (k : ℕ) : c ^ k ∈ PowTripleSet a b c`
  - `mul_mem_powTripleSet : {a b c m n : ℕ}`
  - `powTripleSet_swap12 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet b a c`
  - `powTripleSet_swap23 : (a b c : ℕ) : PowTripleSet a b c = PowTripleSet a c b`
  - `brown_completeness_criterion : (f : ℕ → ℕ) (hf0 : f 0 = 1)`
  - `powTripleSet_2bc_dComplete : (b c : ℕ) :`
  - `pow_ne_pow_of_coprime : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)`
  - `irrational_log_ratio : {a b : ℕ} (ha : 1 < a) (hb : 1 < b)`
- unresolved goals:
  - `exists_close_pair:     (hab : Nat.Coprime a b) :
    ∃ p q : ℕ, 0 < p ∧ b ^ q < a ^ p ∧ a ^ p ≤ 2 * b ^ q := by
  sorry`
  - `powPair_eventually_dense:     ∃ N₀ : ℕ, ∀ M : ℕ, N₀ ≤ M →
      ∃ i j : ℕ, M < a ^ i * b ^ j ∧ a ^ i * b ^ j ≤ 2 * M := by
  s`
  - `erdos_123_d_complete_sequences:     exact powTripleSet_2bc_dComplete a b
  -- All of a, b, c ≥ 3: requires density of smooth numbers`
  - `set equality by extensionality. For any n: n ∈ PowTripleSet a b c ↔ ∃ i j k, n = a^i * b^j * c^k ↔ ∃ j i k, n = b^j * a^i * c^k (swap i,j and use commutativity of multiplication: a^i * b^j = b^j * a^i) ↔ n ∈ PowTripleSet b a c. Use ext, constructor, rintro, and mul_comm.`
- proof traces:
  - `have h_diff : m - f (k + 1) ≤ ∑ i ∈ Finset.range (k + 1), f i`
  - `have h_binary : ∃ s : Finset ℕ, (∑ i ∈ s, 2 ^ i) = n`
  - `have h_exp : a ^ q = b ^ p`
  - `depends_on: Filter.Eventually.mono (in isDComplete_of_antichain)`
  - `depends_on: hA.mono (in isDComplete_mono)`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stdout.txt` (8766 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin` (8941 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/ANALYSIS.md` (5790 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/ARISTOTLE_SUMMARY_a554206b-b500-4e66-8e51-469b5ef6a2f1.md` (2675 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/Main.lean` (14017 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lake-manifest.json` (3109 bytes)
  - `toml` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lakefile.toml` (174 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lean-toolchain` (25 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/ARISTOTLE_SUMMARY_a554206b-b500-4e66-8e51-469b5ef6a2f1.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/Main.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/ANALYSIS.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/lakefile.toml`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_result_a554206b-b500-4e66-8e51-469b5ef6a2f1.bin.contents/e7ffb40d-1e42-444e-8ffd-4d486f55a51e_aristotle/README.md`
- evaluation total: 234.095
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### b1167253-8940-4176-b5b6-fc4968f3735f

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `stalled`
- proof outcome: `partial`
- blocker: `unknown`
- external job id: `37d91660-f818-4cf0-94cf-aaad55620324`
- external status: `COMPLETE`
- objective: Fill in all sorries. The assumption 'the representation is required only for sufficiently large integers' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'the representation is required only for sufficiently large integers' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=COMPLETE; verification_status=partial; theorem_status=partially_verified; blocker=unknown; proved=9; generated=2; subgoals=1
- new signal count: 11
- reused signal count: 5
- generated lemmas:
  - `h_ge_3 : ∀ y ∈ s, y ≥ 3`
  - `erdos_123_d_complete_sequences [sorry at line 148]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proved lemmas:
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `IsDCompleteAll : (A : Set ℕ) : Prop`
  - `powTripleSet_357_no_two : : 2 ∉ PowTripleSet 3 5 7`
  - `powTripleSet_357_ge_three : {n : ℕ} (hn : n ∈ PowTripleSet 3 5 7) (hn2 : n ≥ 2) :`
  - `no_antichain_sum_two : (s : Finset ℕ) (hsub : (↑s : Set ℕ) ⊆ PowTripleSet 3 5 7)`
  - `erdos_123_modified_false : :`
- candidate lemmas:
  - `h_ge_3 : ∀ y ∈ s, y ≥ 3`
  - `erdos_123_d_complete_sequences [sorry at line 148]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
  - `PowTripleSet : (a b c : ℕ) : Set ℕ`
  - `PairwiseCoprime3 : (a b c : ℕ) : Prop`
  - `IsDivisionAntichain : (s : Finset ℕ) : Prop`
  - `IsDComplete : (A : Set ℕ) : Prop`
  - `IsDCompleteAll : (A : Set ℕ) : Prop`
  - `powTripleSet_357_no_two : : 2 ∉ PowTripleSet 3 5 7`
  - `powTripleSet_357_ge_three : {n : ℕ} (hn : n ∈ PowTripleSet 3 5 7) (hn2 : n ≥ 2) :`
  - `no_antichain_sum_two : (s : Finset ℕ) (hsub : (↑s : Set ℕ) ⊆ PowTripleSet 3 5 7)`
  - `erdos_123_modified_false : :`
- unresolved goals:
  - `erdos_123_d_complete_sequences:       PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry`
- proof traces:
  - `have h_ge_3 : ∀ y ∈ s, y ≥ 3`
  - `depends_on: h2 (in no_antichain_sum_two)`
  - `depends_on: absurd (in no_antichain_sum_two)`
  - `depends_on: no_antichain_sum_two (in erdos_123_modified_false)`
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stdout.txt` (8766 bytes)
  - `bin` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin` (5440 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/ARISTOTLE_SUMMARY_37d91660-f818-4cf0-94cf-aaad55620324.md` (2630 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/AristotleWorkspace.lean` (7761 bytes)
  - `md` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/README.md` (248 bytes)
  - `json` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lake-manifest.json` (3109 bytes)
  - `lean` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lakefile.lean` (213 bytes)
  - `bak` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lakefile.toml.bak` (206 bytes)
  - `file` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lean-toolchain` (25 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_stderr.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lake-manifest.json`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lakefile.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/ARISTOTLE_SUMMARY_37d91660-f818-4cf0-94cf-aaad55620324.md`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lean-toolchain`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/AristotleWorkspace.lean`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/lakefile.toml.bak`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_result_37d91660-f818-4cf0-94cf-aaad55620324.bin.contents/b1167253-8940-4176-b5b6-fc4968f3735f_aristotle/README.md`
- evaluation total: 97.39
- notes: Aristotle result downloaded successfully. Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.

### e09e11d5-cf0f-4033-a866-668dd1a6cdff

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `f22db0dd-8b5b-494e-9520-99baef7cdd64`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. The assumption 'a, b, c are integers greater than 1' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'a, b, c are integers greater than 1' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e09e11d5-cf0f-4033-a866-668dd1a6cdff/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e09e11d5-cf0f-4033-a866-668dd1a6cdff/aristotle_list_stdout.txt` (8766 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e09e11d5-cf0f-4033-a866-668dd1a6cdff/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e09e11d5-cf0f-4033-a866-668dd1a6cdff/aristotle_list_stderr.txt`
- notes: Aristotle job f22db0dd-8b5b-494e-9520-99baef7cdd64 is still in progress.

### abd99d04-1751-4f5c-a802-c4d16072db93

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `33d6bd02-cbb8-4418-97f5-4b6732939093`
- external status: `QUEUED`
- objective: Fill in all sorries. The assumption 'summands are distinct' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'summands are distinct' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/abd99d04-1751-4f5c-a802-c4d16072db93/aristotle_submit_stderr.txt` (54 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/abd99d04-1751-4f5c-a802-c4d16072db93/aristotle_submit_stdout.txt` (0 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/abd99d04-1751-4f5c-a802-c4d16072db93/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/abd99d04-1751-4f5c-a802-c4d16072db93/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

## Incidents

- `warning` `repeated_provider_failures`: Provider-side failures reached 7 in recent completed experiments.
- `warning` `retry_budget_exhausted`: Experiment e7ffb40d-1e42-444e-8ffd-4d486f55a51e reached retry budget (6 attempts).
- `warning` `retry_budget_exhausted`: Experiment b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21 reached retry budget (12 attempts).
- `warning` `retry_budget_exhausted`: Experiment bff4c05f-d103-47ac-83f8-1164972a1bca reached retry budget (13 attempts).

## Audit Trail

- `experiment_finalized` at `2026-03-31T05:22:40.931908+00:00`
- `result_ingested` at `2026-03-31T05:22:40.921415+00:00`
- `experiment_finalized` at `2026-03-31T05:22:39.218470+00:00`
- `result_ingested` at `2026-03-31T05:22:39.198618+00:00`
- `experiment_finalized` at `2026-03-31T03:19:20.435878+00:00`
- `result_ingested` at `2026-03-31T03:19:20.422050+00:00`
- `experiment_finalized` at `2026-03-31T01:48:01.941869+00:00`
- `result_ingested` at `2026-03-31T01:48:01.926858+00:00`
- `experiment_finalized` at `2026-03-31T01:48:00.291717+00:00`
- `result_ingested` at `2026-03-31T01:48:00.274085+00:00`

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 11
- jobs synced: 1
- jobs submitted: 1
- active before: 1
- active after: 2
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=10, subgoals=1, traces=0
- synced `e09e11d5-cf0f-4033-a866-668dd1a6cdff` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- queued `abd99d04-1751-4f5c-a802-c4d16072db93` for `erdos-123` via `perturb_assumption` / `legacy.perturb_assumption` (chosen by deterministic fallback policy; move_family=legacy.perturb_assumption; rationale=Assumption 'summands are distinct' has not yet been stress-tested under verification pressure.)
- selected `abd99d04-1751-4f5c-a802-c4d16072db93` rank=1 score=197.45
- considered `93fde400-eb0b-4952-ba2b-50353a8dabe6` rank=2 score=192.45
- considered `80749a44-6708-47b3-a661-9095e629eb2d` rank=3 score=206.897
- considered `16dd55d6-9168-4083-bc5f-6929c3438d63` rank=4 score=201.475
- considered `b5e5c64d-3f3c-4e35-be8b-7896c9280d78` rank=5 score=201.62
- skipped `93fde400-eb0b-4952-ba2b-50353a8dabe6` for `erdos-123` (duplicate active experiment signature)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
