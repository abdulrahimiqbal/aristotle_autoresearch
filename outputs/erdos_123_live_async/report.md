# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 7
- Succeeded: 0
- Stalled: 5
- Failed: 0
- Pending: 2

## Campaign Health

- active=2 pending=2 running=2 completed=5 failed=0
- structured ingestion success rate: 1.0
- semantic reuse rate: 0.101
- transfer usage rate: 0.4
- reusable structure rate: 0.6
- obstruction discovery rate: 0.6
- high-priority frontier share: 0.538
- repeated no-signal streak: 0
- duplicate frontier pressure: 2
- move-family diversity: frontier=9 completed=5
- open incidents: 3

## Version Drift

- `manifest_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `prompt_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `move_registry_version` historical=`2026.03.phase4` current=`2026.03.phase7` count=26
- `runtime_policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26

## Discovery Graph

- nodes: 59
- edges: 64
- verified-like nodes: 30
- `experiment` `9941d619-a8ab-4ac9-ab9c-1503088b4e65` confidence=1.0 provenance=execution
- `experiment` `ddb1aae2-1b93-438c-9165-39a34b6f05c6` confidence=1.0 provenance=execution
- `experiment` `bff4c05f-d103-47ac-83f8-1164972a1bca` confidence=1.0 provenance=execution
- `experiment` `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` confidence=1.0 provenance=execution
- `experiment` `456ae293-4a69-4679-b093-913c49b3b304` confidence=1.0 provenance=execution
- `verified_lemma` `PowTripleSet : (a b c : ℕ) : Set ℕ` confidence=0.95 provenance=artifact
- `verified_lemma` `PairwiseCoprime3 : (a b c : ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `IsDivisionAntichain : (s : Finset ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `IsDComplete : (A : Set ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :` confidence=0.95 provenance=artifact

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

- `IN_PROGRESS`: 2

## Recently completed

- `456ae293-4a69-4679-b093-913c49b3b304` on `erdos-123` -> `stalled`
- `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` on `erdos-123` -> `stalled`
- `bff4c05f-d103-47ac-83f8-1164972a1bca` on `erdos-123` -> `stalled`
- `ddb1aae2-1b93-438c-9165-39a34b6f05c6` on `erdos-123` -> `stalled`
- `9941d619-a8ab-4ac9-ab9c-1503088b4e65` on `erdos-123` -> `stalled`

## Recurring lemmas

- `IsDComplete : (A : Set ℕ) : Prop` — reuse=6
- `IsDivisionAntichain : (s : Finset ℕ) : Prop` — reuse=6
- `PairwiseCoprime3 : (a b c : ℕ) : Prop` — reuse=6
- `PowTripleSet : (a b c : ℕ) : Set ℕ` — reuse=6
- `promoted_lemma : True` — reuse=4
- `IsDComplete_mono [sorry at line 215]: the foundation for any future formal proof.

The sorry here represents the core open mathematical content, not a gap in
the formalization infrastructure. -/` — reuse=2
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
- `c_mem_PowTripleSet : (a b c : ℕ) : c ∈ PowTripleSet a b c` — reuse=2
- `coprime_pow_triple_incomparable : {a b c : ℕ}` — reuse=2
- `cross_family_incomparable : {a b c : ℕ}` — reuse=2
- `diagonal_antichain : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `dvd_iff_exponents_le : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 204]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry` — reuse=2
- `erdos_123_d_complete_sequences [sorry at line 221]: PairwiseCoprime3 a b c →
      IsDComplete (PowTripleSet a b c) := by
  sorry` — reuse=2
- `erdos_123_no_coprimality_false [sorry at line 200]: --       PairwiseCoprime3 a b c →
--       IsDComplete (PowTripleSet a b c) := by
--   sorry` — reuse=2
- `exponent_map_injective : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
- `h_card_eq_one : s.card = 1` — reuse=2
- `h_card_le_one : s.card ≤ 1` — reuse=2
- `h_contra : b ^ j₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂` — reuse=2
- `h_div : a ^ i₁ * b ^ j₁ * c ^ k₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂ ∧ a ^ i₂ * b ^ j₂ * c ^ k₂ ∣ a ^ i₁ * b ^ j₁ * c ^ k₁` — reuse=2
- `h_div : i₁ ≤ i₂ ∧ j₁ ≤ j₂ ∧ k₁ ≤ k₂ ∧ i₂ ≤ i₁ ∧ j₂ ≤ j₁ ∧ k₂ ≤ k₁` — reuse=2
- `h_div_a : a ^ i₁ ∣ a ^ i₂ * b ^ j₂ * c ^ k₂` — reuse=2
- `h_div_c : c ^ (k₁ - k₂) ∣ a ^ i₂ * b ^ j₂` — reuse=2
- `h_div_one : c ^ (k₁ - k₂) ∣ 1` — reuse=2
- `h_factor_a : a ^ i₁ ∣ a ^ i₂` — reuse=2
- `h_factor_b : b ^ j₁ ∣ b ^ j₂` — reuse=2
- `h_factor_c : c ^ k₁ ∣ c ^ k₂` — reuse=2
- `hcop : Nat.Coprime (a ^ (i₁ - i₂)) (b ^ j₂ * c ^ k₂)` — reuse=2
- `hs_powers_of_two : ∀ x ∈ s, ∃ m : ℕ, x = 2 ^ m` — reuse=2
- `hs_sum_powers_of_two : ∃ m : ℕ, s.sum id = 2 ^ m` — reuse=2
- `not_eventually_pow2 : :` — reuse=2
- `one_mem_PowTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c` — reuse=2
- `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :` — reuse=2
- `pow2_antichain_card_le_one : (s : Finset ℕ)` — reuse=2
- `powTripleSet_222_eq : : PowTripleSet 2 2 2 = {n | ∃ m : ℕ, n = 2 ^ m}` — reuse=2
- `powTripleSet_222_not_dComplete : :` — reuse=2
- `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :` — reuse=2
- `pow_b_mem : {a b c : ℕ} (ha : 0 < a) (hc : 0 < c) (j : ℕ) :` — reuse=2
- `pow_c_mem : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (k : ℕ) :` — reuse=2
- `product_mem : {a b c : ℕ} (i j k : ℕ) :` — reuse=2

## Space Search Progress

- recurring lemmas: 51 clusters
- recurring subgoals: 1 clusters
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- recurring lemmas are beginning to cluster across runs
- repeated subgoal `erdos_123_d_complete_sequences: pairwisecoprime3 v v v → isdcomplete (powtripleset v v v) := by sorry` across 2 runs
- no blocker patterns aggregated yet
- move `promote_lemma` repeatedly yields blocker `unknown` / `partial` (3 runs)

## Assumption sensitivity

- `a, b, c are pairwise coprime` — avg_sensitivity=0.2 across 1 observations

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
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `a554206b-b500-4e66-8e51-469b5ef6a2f1`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. The assumption 'no chosen summand divides another' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'no chosen summand divides another' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stdout.txt` (8756 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_list_stderr.txt`
- notes: Aristotle job a554206b-b500-4e66-8e51-469b5ef6a2f1 is still in progress.

### b1167253-8940-4176-b5b6-fc4968f3735f

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `in_progress`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `37d91660-f818-4cf0-94cf-aaad55620324`
- external status: `IN_PROGRESS`
- objective: Fill in all sorries. The assumption 'the representation is required only for sufficiently large integers' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'the representation is required only for sufficiently large integers' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=IN_PROGRESS; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stdout.txt` (8756 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/b1167253-8940-4176-b5b6-fc4968f3735f/aristotle_list_stderr.txt`
- notes: Aristotle job 37d91660-f818-4cf0-94cf-aaad55620324 is still in progress.

## Incidents

- `warning` `repeated_provider_failures`: Provider-side failures reached 5 in recent completed experiments.
- `warning` `retry_budget_exhausted`: Experiment b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21 reached retry budget (12 attempts).
- `warning` `retry_budget_exhausted`: Experiment bff4c05f-d103-47ac-83f8-1164972a1bca reached retry budget (13 attempts).

## Audit Trail

- `experiment_finalized` at `2026-03-31T03:19:20.435878+00:00`
- `result_ingested` at `2026-03-31T03:19:20.422050+00:00`
- `experiment_finalized` at `2026-03-31T01:48:01.941869+00:00`
- `result_ingested` at `2026-03-31T01:48:01.926858+00:00`
- `experiment_finalized` at `2026-03-31T01:48:00.291717+00:00`
- `result_ingested` at `2026-03-31T01:48:00.274085+00:00`
- `experiment_finalized` at `2026-03-31T00:34:30.555919+00:00`
- `result_ingested` at `2026-03-31T00:34:30.550974+00:00`
- `experiment_finalized` at `2026-03-30T23:56:33.332007+00:00`
- `result_ingested` at `2026-03-30T23:56:33.322940+00:00`

## Latest manager decision

- policy path: `fallback`
- policy candidate audits: 13
- jobs synced: 2
- jobs submitted: 0
- active before: 2
- active after: 2
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=10, subgoals=1, traces=0
- synced `e7ffb40d-1e42-444e-8ffd-4d486f55a51e` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- synced `b1167253-8940-4176-b5b6-fc4968f3735f` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- considered `506ed338-67ae-4123-a368-03c0953a6a27` rank=1 score=181.6921
- considered `5c9d6158-1646-4e1c-9386-2a1f3c2587c9` rank=2 score=181.6921
- considered `df1f4898-225b-4006-a093-3f4ae90e1bcb` rank=3 score=186.1921
- considered `82c4af76-19fa-4506-8ee9-a910c9bf8290` rank=4 score=186.1921
- considered `7cdd6b26-7d97-4dac-baa5-e700ef2abe63` rank=5 score=195.6391
- skipped `7cdd6b26-7d97-4dac-baa5-e700ef2abe63` for `erdos-123` (conjecture active cap reached)
- skipped `a98ae23e-f212-4899-92b9-7145a28bae29` for `erdos-123` (conjecture active cap reached)
- skipped `404c0682-1e4e-4c09-800d-a38f38003196` for `erdos-123` (conjecture active cap reached)
- skipped `8d5e4905-623a-4f8c-ade0-3a9aecc5ab2e` for `erdos-123` (conjecture active cap reached)
- skipped `586d0b87-dd66-45cc-8090-7da2299d891c` for `erdos-123` (conjecture active cap reached)
- skipped `664aabcc-390c-4983-bdd8-631a27c82ca9` for `erdos-123` (conjecture active cap reached)
- skipped `b805302c-1ca2-4caa-87f2-9dd7527cf1a8` for `erdos-123` (conjecture active cap reached)
- skipped `ea8c8f32-5e08-4229-af3f-b9d69cce0f12` for `erdos-123` (conjecture active cap reached)
- skipped `506ed338-67ae-4123-a368-03c0953a6a27` for `erdos-123` (duplicate active experiment signature)
- skipped `5c9d6158-1646-4e1c-9386-2a1f3c2587c9` for `erdos-123` (duplicate active experiment signature)
- skipped `df1f4898-225b-4006-a093-3f4ae90e1bcb` for `erdos-123` (conjecture active cap reached)
- skipped `82c4af76-19fa-4506-8ee9-a910c9bf8290` for `erdos-123` (conjecture active cap reached)
- skipped `0d46973a-d6ce-427c-9d64-9b0620adcd22` for `erdos-123` (conjecture active cap reached)

## Suggested next move

- Promote the top recurring lemma into a standalone theorem if not already tested.
