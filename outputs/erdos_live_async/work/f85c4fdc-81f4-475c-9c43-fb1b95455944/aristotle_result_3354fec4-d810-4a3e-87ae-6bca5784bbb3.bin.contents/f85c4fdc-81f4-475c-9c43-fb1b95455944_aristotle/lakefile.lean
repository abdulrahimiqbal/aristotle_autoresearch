import Lake
open Lake DSL

package «AristotleWorkspace» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib «AristotleWorkspace» where

lean_lib «Main» where

require mathlib from ".lake" / "packages" / "mathlib"
