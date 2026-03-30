import Lake
open Lake DSL

package «RequestProject» where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib «Main» where

require "leanprover-community" / "mathlib" @ git "main"
