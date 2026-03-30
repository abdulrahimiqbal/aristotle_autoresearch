import Lake
open Lake DSL

package «RequestProject» where
  leanOptions := #[⟨`autoImplicit, false⟩]

require "leanprover-community" / "mathlib"

@[default_target]
lean_lib «Main» where
