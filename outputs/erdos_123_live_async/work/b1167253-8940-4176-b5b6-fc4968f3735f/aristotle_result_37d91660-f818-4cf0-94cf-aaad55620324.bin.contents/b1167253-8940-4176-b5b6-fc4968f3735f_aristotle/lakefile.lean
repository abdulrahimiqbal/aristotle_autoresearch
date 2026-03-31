import Lake
open Lake DSL

package RequestProject where
  leanOptions := #[⟨`autoImplicit, false⟩]

require "leanprover-community" / "mathlib" @ git "main"

@[default_target]
lean_lib AristotleWorkspace where
