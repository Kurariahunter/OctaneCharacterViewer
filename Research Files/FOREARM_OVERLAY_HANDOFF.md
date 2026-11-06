# PC Elsa forearm overlays — 2026-10-22

Update: FULL_PALETTE_IDLES_HANDOFF.md records full62-bone previews for all three specific idles and their coverage audit.

Opt-in evaluated animation:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-full-palette.json`

Adds Forearm_OL_Left and Forearm_OL_Right source paths to the preceding eye/lid/facial IdleC preview. This closes the two palette bind-offset fallbacks for this bounded rig/clip fixture. Full palette coverage does not mean complete engine recreation or live-game parity. Defaults remain unchanged, and the running index-finger issue is separate.

## Source graph

Skin outputs507/514 are TransformDilationWithTransform. Their local orientations derive from wrist rotor inputs via RotorToEulerZXYVariantProcessor, Euler Z decomposition, FloatMultiply with source controls854/855, Euler Z composition and EulerZXYToRotorVariantProcessor. Existing native Transform conversion places the result in its rig space. No empirical twist factor was introduced.

Rotor-to-Euler registration0x501D70 binds factory0x4F8B30. Factory0x4EB9D0 allocates constructor0x4DF6F0, vtable0x1B2F78C. Execute+0x40 is0x4DF750, which calls0x40D8B0. The evaluator runs this original PC execute routine using explicit input/output node fixtures.

FloatMultiply registration0x5020FD binds0x54B4F0. Allocation chain0x54B4C0 ->0x545CC0 ->0x53FB90 ->constructor0x539960 assigns vtable0x1B342DC; execute+0x40 is0x52D540. The graph uses its observed two-input form.

Disassembly: ElsaSceneResearch/ControllerState/forearm-twist-disassembly.txt.

## Validation

103 native rotor/Euler round trips include identity, both exact X singular angles, and100 seeded mixed Euler triples. Compare reconstructed rotation matrices, since equivalent Euler representations need not have equal angles. Maximum rotation-matrix component error7.214112548226126e-6. The103 native two-input products match float32 products exactly.

Test: ElsaSceneResearch/test_pc_forearm_twist.py. Report: ControllerState/forearm-twist-validation.json. Native Euler conversion and explicit products are tested; scene scheduling, arbitrary runtime variant bindings and live visual parity are not inferred from those tests.

The bake and comparison reports are saved beside the preview. `compare_forearm_paths.py` requires every non-overlay palette matrix to remain exactly equal to the preceding native-idleC-eye-paths.json artifact.

Completed bake:62 source bones/62 palette bones,303 simulation frames,152 saved samples. Existing endpoint/native-matrix/shear/dress checks pass. Only the two overlay bones change, in152 samples; all other matrices are identical. Maximum matrix-component difference0.9068673644214869 is not an angular or visual error score. No visual confirmation of this new overlay preview has yet been supplied.

Reproduce using the EYE_DIRECTION_HANDOFF.md command, change output to the full-palette filename above and append `--native-forearm-paths`.

## Next

Visually check forearm deformation in this IdleC preview. Then extend the same full-palette fixture to the other Elsa idles to check broader source graph coverage. Native animation state scheduling, default channel policies, secondary-motion context and game comparisons remain work beyond palette coverage.
