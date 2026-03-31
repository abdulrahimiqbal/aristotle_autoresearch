import Lake
open Lake DSL

package «request-project» where
  version := v!"0.1.0"
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib Main where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.28.0"
