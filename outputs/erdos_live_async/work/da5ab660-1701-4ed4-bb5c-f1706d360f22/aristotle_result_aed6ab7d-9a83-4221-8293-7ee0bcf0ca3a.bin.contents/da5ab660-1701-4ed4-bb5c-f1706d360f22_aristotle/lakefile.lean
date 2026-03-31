import Lake
open Lake DSL

package «RequestProject»

@[default_target]
lean_lib «AristotleWorkspace» where

require mathlib from ".lake" / "packages" / "mathlib"
