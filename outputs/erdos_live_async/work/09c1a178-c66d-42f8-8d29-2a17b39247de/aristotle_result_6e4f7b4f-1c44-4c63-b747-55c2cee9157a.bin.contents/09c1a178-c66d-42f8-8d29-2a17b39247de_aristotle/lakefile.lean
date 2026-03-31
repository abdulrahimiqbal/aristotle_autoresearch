import Lake
open Lake DSL

package «AristotleWorkspace» where
  version := v!"0.1.0"
  leanOptions := #[⟨`autoImplicit, false⟩]

require "leanprover-community" / "mathlib" @ git "main"

@[default_target]
lean_lib «Main» where
