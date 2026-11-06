# PC Elsa native eyelid paths — 2026-10-22

Update: eye direction now has an additional opt-in native bake. See EYE_DIRECTION_HANDOFF.md; the original eyelid-only artifact below is preserved.

Open evaluated animation in the viewer and choose:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-eyelid-paths.json`

This opt-in IdleC preview includes the previous eight facial paths plus four source eyelid paths. It evaluates 58 source bones in the 62-bone palette. Startup/default playback is unchanged. No empirical eyelid pose offsets were added.

## Verified PC path

The four lids ultimately depend on RelationshipProcessor177, RelationshipData node34. Its 612-byte blob SHA256 is `7ad4d7ac5ad56a235376973be6fd8849ac5e68d27d1ece72d96d04a1f25216b3`. Inputs are341,342,343,340; Dilation outputs are274,278,282,286. Existing orientation connections feed the final lid skin outputs825,822,831,828.

The original PC full processor0x54C9A0 was compared with the original separate input evaluation0x544E00, record accessor0x503E00, and output writer0x53D2B0. All61 cases match exactly: neutral, individual-axis values within[-100,100], and40 seeded mixed cases. Outputs remain finite unit rotors with zero translation and unit scale. The graph adapter accepts this exact blob hash; unknown relationships still fail.

Both paths use explicit zero segment caches and identity initial Dilation outputs. Agreement validates bounded execution of this file data, not independent correctness of fixture initialization, persistent runtime caches, or live visual parity. The new PS4/Wii U executables remain cross-platform references; this behavior was tested directly in the hash-pinned PC executable, without assuming platform layouts match.

## Preview validation

The303 simulation frames produce152 saved samples. Palette/native-matrix/dress checks pass: max endpoint error8.959200081264404e-6, native matrix error2.868473529815674e-7, TRS shear1.4474200428022767e-7, dress root error0, dress segment error3.068858056287649e-7.

Comparison against `native-idleC-facial-paths.json` changes exactly the four eyelid bones in152 samples; every other palette matrix is identical. Maximum matrix-component difference0.5611001798765274 is a difference, not a visual error score. No screenshot or live-game eyelid comparison has been performed.

Reproduce using the command in FACIAL_GRAPH_HANDOFF.md, change the output filename above, and append `--native-eyelid-paths`. Run `ElsaSceneResearch/test_pc_eyelid_relationship.py` and `OctaneCharacterViewer/compare_eyelid_paths.py` for the bounded checks. Reports are `ControllerState/eyelid-relationship-validation.json` and `NativePreviews/eyelid-paths-comparison.json`.

## Next boundary

Eye-direction paths still stop at TransformVectorWithDilation outputs799 and813. Resolve that native operation next, then compare facial motion visually with the game. Automatic scheduling/default policies and the running-index-finger issue are separate unresolved work.
