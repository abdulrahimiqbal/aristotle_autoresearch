# Summary of changes
All sorries have been filled in and the theorem has been split into two parts:

1. **Bridge lemma** (`sidon_self_union`): Captures the recurring subgoal from the Erdős–Turán Sidon-extension argument — that the Sidon property is preserved under self-union (`S ∪ S`). This follows from `Finset.union_idempotent` (since `S ∪ S = S`).

2. **Main theorem** (`promoted_lemma`): The remaining reduction to `True`, which is trivially discharged once the bridge lemma handles the Sidon-preservation subgoal.

Additionally, `IsSidonFinset` was formalized as the standard B₂-set definition (all pairwise sums are distinct). The project builds cleanly with no sorries and only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).

The lakefile was updated to Lake v5 TOML format (required by Lean 4.28.0) and `Main.lean` was added as a build target.