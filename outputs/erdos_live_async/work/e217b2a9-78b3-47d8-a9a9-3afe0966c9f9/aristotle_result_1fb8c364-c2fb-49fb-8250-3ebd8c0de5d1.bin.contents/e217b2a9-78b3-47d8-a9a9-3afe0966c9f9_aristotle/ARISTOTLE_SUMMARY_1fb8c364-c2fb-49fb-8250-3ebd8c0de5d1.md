# Summary of changes
## Fragility Analysis & Falsifying Witness for Erdős Problem 181

I identified the **most fragile observed variant** as the original `erdos_181_hypercube_ramsey` theorem, whose fragility stems from two placeholder definitions:

- `IsHypercubeGraph n G := True` — any graph qualifies as a "hypercube"
- `GraphRamseyNumber G := 0` — the Ramsey number is identically zero

### What was done (in `Main.lean`):

1. **Proved the original theorem** (`erdos_181_hypercube_ramsey`): Demonstrated that with the placeholder definitions, the statement is trivially true — just pick `C = 1` and `G = ⊥` (the empty graph). This one-line proof (`⟨1, by norm_num, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩`) serves as the **fragility witness**, showing the formalization imposes no real mathematical constraint.

2. **Constructed a falsifying witness** (`no_linear_bound_on_bad_ramsey`): Defined `BadRamseyNumber n := (2^n)^2` and formally proved that no constant `C` can satisfy `BadRamseyNumber n ≤ C * 2^n` for all `n`. The key argument: if `(2^n)^2 ≤ C * 2^n` for all `n`, canceling `2^n > 0` gives `2^n ≤ C` for all `n`, contradicting unboundedness of `2^n`. This identifies the **linear-in-`2^n` conclusion** as the most fragile part of the Erdős 181 statement — it breaks under any super-linear Ramsey number growth.

All three theorems compile without `sorry`, use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`), and are verified by `lake build`.