import Lake
open Lake DSL

package «AristotleWorkspace» where
  leanOptions := #[⟨`autoImplicit, false⟩]

require mathlib from ".lake" / "packages" / "mathlib"

@[default_target]
lean_lib «AristotleWorkspace» where
