import Lake
open Lake DSL

package AristotleWorkspace where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib Main where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"
