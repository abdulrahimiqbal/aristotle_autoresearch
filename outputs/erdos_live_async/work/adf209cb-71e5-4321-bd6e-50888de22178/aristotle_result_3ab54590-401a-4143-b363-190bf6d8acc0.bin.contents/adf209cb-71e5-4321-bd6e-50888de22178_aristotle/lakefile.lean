import Lake
open Lake DSL

package RequestProject where
  leanOptions := #[]

@[default_target]
lean_lib AristotleWorkspace

require mathlib from ".lake" / "packages" / "mathlib"
