# Skin rig display port

Source: user-supplied DI3StaticConverter_MaterialFallbackFix.zip, Editor/DI3RigReader.cs.
Ported inverse bind-matrix reconstruction, merging by bone name with bind-pose consistency checks, BasisPool matching, ancestor traversal, and cycle checks into System.Numerics-based PreviewRig.cs.

No Unity runtime dependency. No helper-parent guesses copied. Missing verified parents remain roots. No vertex skin-weight decoding or animation added by this display port.

Actual PC Elsa OCT: 62 bind bones, 42 verified parent links. Remaining links are deliberately unresolved rather than inferred. Build: 0 errors, 17 warnings. Grimm pieces still falls back to recorded rigid scene nodes because it has no bind influences.

Updated executable: RigTextureBuild/AssetWiiUdio.exe.
