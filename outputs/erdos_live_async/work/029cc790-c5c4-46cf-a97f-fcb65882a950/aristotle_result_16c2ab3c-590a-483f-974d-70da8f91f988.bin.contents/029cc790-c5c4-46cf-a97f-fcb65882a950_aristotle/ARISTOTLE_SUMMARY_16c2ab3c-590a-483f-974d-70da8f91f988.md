# Summary of changes
## Fragility Witness for Erdős Problem 181 Formulation

The project contained a Lean formalization of Erdős Problem 181 (hypercube Ramsey numbers) with two placeholder definitions:

- `IsHypercubeGraph n G := True` — accepts any graph as a "hypercube"
- `GraphRamseyNumber G := 0` — assigns Ramsey number 0 to every graph

### What I did

I produced a **falsifying witness for the meaningfulness** of this formulation by proving the theorem trivially:

```lean
exact ⟨1, le_refl 1, fun n => ⟨⊥, trivial, Nat.zero_le _⟩⟩
```

This one-line proof demonstrates the fragility: choose `C = 1`, pick the empty graph `⊥` for every `n`, observe that `IsHypercubeGraph` is trivially `True`, and that `GraphRamseyNumber` returns `0 ≤ 1 * 2^n`. The proof carries **zero** Ramsey-theoretic content.

### Fragility analysis (in the file's docstring)

Two independent degeneracies make the theorem vacuous:

1. **`IsHypercubeGraph`** ignores its graph argument entirely (Lean even emits an "unused variable" warning), so the existential can pick any graph — including the trivial empty graph `⊥`.

2. **`GraphRamseyNumber`** ignores its graph argument entirely, returning `0`, so the upper bound `0 ≤ C * 2^n` holds for all `C ≥ 0`.

### What a non-fragile formulation would require

A faithful `IsHypercubeGraph` asserting graph-isomorphism to the actual hypercube Q_n (vertices `Fin n → Bool`, adjacency = Hamming distance 1), and a correct `GraphRamseyNumber` computing the minimum N such that every 2-colouring of K_N's edges contains a monochromatic copy of the input graph. With those in place, the statement becomes a genuine open problem.

### Verification

- The file `Main.lean` builds successfully with no `sorry`.
- `#print axioms` confirms only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).