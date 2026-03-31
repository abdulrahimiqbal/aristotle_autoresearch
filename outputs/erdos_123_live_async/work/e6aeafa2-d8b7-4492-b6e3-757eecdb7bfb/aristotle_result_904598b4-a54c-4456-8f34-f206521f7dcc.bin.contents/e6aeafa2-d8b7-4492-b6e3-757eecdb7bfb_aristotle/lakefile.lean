import Lake
open Lake DSL

package AristotleWorkspace where
  leanOptions := #[]

@[default_target]
lean_lib AristotleWorkspace where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"
