import Lake
open Lake DSL

package «AristotleWorkspace» where
  version := v!"0.1.0"

require "leanprover-community" / "mathlib" @ git "main"

@[default_target]
lean_lib «AristotleWorkspace» where
  srcDir := "."
