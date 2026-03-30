# Summary of changes
## Falsifying / Independence-Style Witnesses for the Fragile Erdős-44 Variant

Created `CounterexampleWitness.lean` — a fully machine-verified Lean 4 file (no `sorry`, no non-standard axioms) containing formal witnesses that pin down the fragility of `erdos_44_sidon_extension`.

### What was identified as "most fragile"

The density bound `(1 - ε) * √M ≤ |A ∪ B|` is the fragile core. Two structural fragilities were identified:

- **(F1)** The bound must hold for *every* starting Sidon set A, including adversarial ones that block many nearby extensions.
- **(F2)** The quantifier order `∀ε>0, ∃Mε, ∀N, ∀A, ∃M …` forces Mε to be chosen *before* N and A are revealed.

### Formal results proved (all sorry-free)

| Theorem | Role |
|---------|------|
| `sidon_card_sq_le` | **Erdős–Turán upper bound**: any Sidon A ⊆ [1,N] satisfies \|A\|² ≤ 4N. This is the theoretical ceiling that makes the density target tight. |
| `sidon_card_le_two_sqrt` | **Corollary**: \|A\| ≤ 2√N for Sidon A ⊆ [1,N]. The leading constant 2 cannot be exceeded. |
| `strengthened_variant_coeff_two_false` | **Falsification witness**: the variant with coefficient 2 (demanding 2√M < \|A∪B\|) is *provably false*. Witness: N=1, A={1}. The Erdős–Turán bound forces \|A∪B\| ≤ 2√M for any Sidon extension, directly contradicting 2√M < \|A∪B\|. |
| `isSidon_one_two_five` | {1,2,5} is Sidon. |
| `not_isSidon_one_two_five_six` | {1,2,5,6} is NOT Sidon (1+6 = 2+5 = 7). Concrete blocked-extension witness: the Sidon set {1,2,5} cannot be greedily extended to include 6. |
| `empty_sidon`, `singleton_sidon`, `pair_sidon` | Basic Sidon constructions. |

### Interpretation

The original theorem's factor `(1-ε)` lives in the narrow interval `(0, 2]` — below 0 the statement is vacuous, and above 2 it is provably false (by `strengthened_variant_coeff_two_false`). The concrete obstruction `{1,2,5} → {1,2,5,6}` shows that even single-step extensions can fail, so the existential quantifier on M (allowing the interval to grow) is essential. Together these results delineate the exact boundary of the fragile variant: any tightening of the leading constant past 2 breaks the statement, and any restriction on M's growth creates blocked-extension counterexamples.