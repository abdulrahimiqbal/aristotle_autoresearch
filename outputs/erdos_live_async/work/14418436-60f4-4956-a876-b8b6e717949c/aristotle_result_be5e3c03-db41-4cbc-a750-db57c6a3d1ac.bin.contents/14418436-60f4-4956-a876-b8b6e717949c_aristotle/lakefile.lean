import Lake
open Lake DSL

package «AristotleWorkspace» where
  version := v!"0.1.0"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"

@[default_target]
lean_lib «Main» where
