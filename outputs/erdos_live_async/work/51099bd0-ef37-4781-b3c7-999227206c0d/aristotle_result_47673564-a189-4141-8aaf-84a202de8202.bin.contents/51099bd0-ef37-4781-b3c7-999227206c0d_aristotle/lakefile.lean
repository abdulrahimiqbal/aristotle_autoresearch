import Lake
open Lake DSL

package AristotleWorkspace where
  version := v!"0.1.0"

@[default_target]
lean_lib Main where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"
