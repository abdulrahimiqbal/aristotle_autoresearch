# Research Report: Hidden-dependency mapping across Erdos combinatorics conjectures

**Project ID:** `erdos-combo-001`

## Overarching problem

Map the hidden dependency structures shared by open Erdos problems in graph Ramsey theory and additive combinatorics, with emphasis on which assumptions trigger recurring lemmas, which perturbations shift the apparent provability boundary, and which formalizations expose reusable infrastructure across the family.

## Summary

- Experiments: 6
- Succeeded: 0
- Stalled: 4
- Failed: 0
- Pending: 2

## Campaign Health

- active=2 pending=2 running=0 completed=4 failed=0
- structured ingestion success rate: 1.0
- semantic reuse rate: 0.082
- transfer usage rate: 0.5
- reusable structure rate: 0.75
- obstruction discovery rate: 0.5
- high-priority frontier share: 0.5
- repeated no-signal streak: 0
- duplicate frontier pressure: 1
- move-family diversity: frontier=9 completed=4
- open incidents: 3

## Version Drift

- `manifest_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `prompt_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26
- `move_registry_version` historical=`2026.03.phase4` current=`2026.03.phase7` count=26
- `runtime_policy_version` historical=`2026.03.phase6` current=`2026.03.phase7` count=26

## Discovery Graph

- nodes: 47
- edges: 49
- verified-like nodes: 24
- `experiment` `9941d619-a8ab-4ac9-ab9c-1503088b4e65` confidence=1.0 provenance=execution
- `experiment` `ddb1aae2-1b93-438c-9165-39a34b6f05c6` confidence=1.0 provenance=execution
- `experiment` `bff4c05f-d103-47ac-83f8-1164972a1bca` confidence=1.0 provenance=execution
- `experiment` `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` confidence=1.0 provenance=execution
- `verified_lemma` `PowTripleSet : (a b c : ℕ) : Set ℕ` confidence=0.95 provenance=artifact
- `verified_lemma` `PairwiseCoprime3 : (a b c : ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `IsDivisionAntichain : (s : Finset ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `IsDComplete : (A : Set ℕ) : Prop` confidence=0.95 provenance=artifact
- `verified_lemma` `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :` confidence=0.95 provenance=artifact
- `verified_lemma` `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :` confidence=0.95 provenance=artifact

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

- `QUEUED`: 2

## Recently completed

- `b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21` on `erdos-123` -> `stalled`
- `bff4c05f-d103-47ac-83f8-1164972a1bca` on `erdos-123` -> `stalled`
- `ddb1aae2-1b93-438c-9165-39a34b6f05c6` on `erdos-123` -> `stalled`
- `9941d619-a8ab-4ac9-ab9c-1503088b4e65` on `erdos-123` -> `stalled`

## Recurring lemmas

- `IsDComplete : (A : Set ℕ) : Prop` — reuse=4
- `IsDivisionAntichain : (s : Finset ℕ) : Prop` — reuse=4
- `PairwiseCoprime3 : (a b c : ℕ) : Prop` — reuse=4
- `PowTripleSet : (a b c : ℕ) : Set ℕ` — reuse=4
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
- `exponent_map_injective : {a b c : ℕ} (ha : 1 < a) (hb : 1 < b) (hc : 1 < c)` — reuse=2
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
- `one_mem_PowTripleSet : (a b c : ℕ) : 1 ∈ PowTripleSet a b c` — reuse=2
- `one_mem_PowTripleSet : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :` — reuse=2
- `pow_a_mem : {a b c : ℕ} (hb : 0 < b) (hc : 0 < c) (i : ℕ) :` — reuse=2
- `pow_b_mem : {a b c : ℕ} (ha : 0 < a) (hc : 0 < c) (j : ℕ) :` — reuse=2
- `pow_c_mem : {a b c : ℕ} (ha : 0 < a) (hb : 0 < b) (k : ℕ) :` — reuse=2
- `product_mem : {a b c : ℕ} (i j k : ℕ) :` — reuse=2

## Space Search Progress

- recurring lemmas: 41 clusters
- recurring subgoals: 1 clusters
- recurring proof traces: none stabilized yet
- no-signal branches: none crossed the backoff threshold

## What we learned

- recurring lemmas are beginning to cluster across runs
- repeated subgoal `erdos_123_d_complete_sequences: pairwisecoprime3 v v v → isdcomplete (powtripleset v v v) := by sorry` across 2 runs
- no blocker patterns aggregated yet
- move `promote_lemma` repeatedly yields blocker `unknown` / `partial` (3 runs)

## Assumption sensitivity

- None yet.

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
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `593ad586-0a26-4254-b2e9-72a6920b2438`
- external status: `QUEUED`
- objective: Fill in all sorries. The assumption 'a, b, c are pairwise coprime' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'a, b, c are pairwise coprime' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stderr.txt` (58 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stdout.txt` (8751 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/456ae293-4a69-4679-b093-913c49b3b304/aristotle_list_stderr.txt`
- notes: Aristotle job 593ad586-0a26-4254-b2e9-72a6920b2438 is still queued.

### e7ffb40d-1e42-444e-8ffd-4d486f55a51e

- move: `perturb_assumption`
- move family: `legacy.perturb_assumption`
- theorem family: `erdos_problem`
- phase: `consolidation`
- status: `submitted`
- proof outcome: `unknown`
- blocker: `unknown`
- external job id: `a554206b-b500-4e66-8e51-469b5ef6a2f1`
- external status: `QUEUED`
- objective: Fill in all sorries. The assumption 'no chosen summand divides another' has been removed. Determine whether the proof still closes and report the blocker if not. Discovery question: Which solved or partially solved special cases transfer to broader triples once we reformulate the obstruction in the right way?
- rationale: Assumption 'no chosen summand divides another' has not yet been stress-tested under verification pressure.
- learned summary: remote_status=QUEUED; verification_status=unknown; theorem_status=unresolved; blocker=unknown
- new signal count: 0
- reused signal count: 0
- artifact inventory:
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_submit_stderr.txt` (54 bytes)
  - `txt` `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_submit_stdout.txt` (0 bytes)
- artifacts:
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_submit_stdout.txt`
  - `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/work/e7ffb40d-1e42-444e-8ffd-4d486f55a51e/aristotle_submit_stderr.txt`
- notes: Submitted Aristotle job without waiting for completion.

## Incidents

- `warning` `repeated_provider_failures`: Provider-side failures reached 4 in recent completed experiments.
- `warning` `retry_budget_exhausted`: Experiment b81e1cdc-4cf1-4713-b2c4-5cb4e5684b21 reached retry budget (12 attempts).
- `warning` `retry_budget_exhausted`: Experiment bff4c05f-d103-47ac-83f8-1164972a1bca reached retry budget (13 attempts).

## Audit Trail

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
- policy candidate audits: 14
- jobs synced: 1
- jobs submitted: 1
- active before: 1
- active after: 2
- report path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.md`
- snapshot path: `/home/runner/work/aristotle_autoresearch/aristotle_autoresearch/outputs/erdos_123_live_async/report.manager_snapshot.json`
- recurring structures considered: lemmas=10, subgoals=1, traces=0
- synced `456ae293-4a69-4679-b093-913c49b3b304` with proof_outcome=`unknown` new_signal=0 reused_signal=0
- queued `e7ffb40d-1e42-444e-8ffd-4d486f55a51e` for `erdos-123` via `perturb_assumption` / `legacy.perturb_assumption` (chosen by deterministic fallback policy; move_family=legacy.perturb_assumption; rationale=Assumption 'no chosen summand divides another' has not yet been stress-tested under verification pressure.)
- selected `e7ffb40d-1e42-444e-8ffd-4d486f55a51e` rank=1 score=189.016
- considered `07459280-17da-4704-a1cd-dc87a4225e95` rank=2 score=189.016
- considered `33cc0a74-4f0b-49dd-ab5f-5fdb2e5cb789` rank=3 score=184.016
- considered `0b546dd6-33c9-4329-aa0f-4d6fc95f002f` rank=4 score=188.516
- considered `177f6bc4-cbe0-4bb3-8cad-950fc0160b3f` rank=5 score=188.516
- skipped `33cc0a74-4f0b-49dd-ab5f-5fdb2e5cb789` for `erdos-123` (duplicate active experiment signature)
- skipped `0b546dd6-33c9-4329-aa0f-4d6fc95f002f` for `erdos-123` (frontier throttled for duplicate move-family pressure)
- skipped `177f6bc4-cbe0-4bb3-8cad-950fc0160b3f` for `erdos-123` (frontier throttled for duplicate move-family pressure)

## Suggested next move

- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.
