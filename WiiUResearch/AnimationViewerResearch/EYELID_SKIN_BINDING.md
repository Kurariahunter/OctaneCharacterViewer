# Eyelid skin binding checkpoint — 2026-10-24

The source-association audit found and corrected swapped upper/lower eyelid labels in the previous world fixture. No numerical angle adjustment was made. The evaluator now follows each source SkinInfluence association backwards through Matrix4x4, world Dilation, orientation connection and generated converter processors. It asserts their types and Head 388 dependency; no eyelid output IDs are hand assigned.

Verified source mappings:

| Bone | Influence | Matrix node |
|---|---:|---:|
| LowerLidLeft | 7 | 828 |
| LowerLidRight | 8 | 825 |
| UpperLidLeft | 10 | 822 |
| UpperLidRight | 11 | 819 |

For each of 12 outputs (four lids, three times), the checker verifies the source influence name, matrix producer and its input. It reads that influence's own inverse bind matrix, checks invertibility, and derives skin = evaluated world @ inverse bind in the existing column convention. Bind cancellation and five test-point roundtrips pass; maximum point residual is 8.881784197001252e-16.

This residual checks algebraic consistency, not agreement with native execution. The Wii U DilationToMatrix4x4 numerical conversion and weighted vertex rendering have not yet been independently validated. These four matrices are a partial palette; do not present them as complete character playback. The production viewer remains unchanged.

Reproduce:
```
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_head_fixture.py
python WiiUResearch/AnimationViewerResearch/validate_eyelid_skin_binding.py
```

Next: resolve the native Dilation-to-Matrix conversion and compare its output with this column convention before rendering the bounded eyelid preview.

Follow-up: NATIVE_MATRIX.md validates the PC conversion and the fixture now exports its packed affine output. The previously stated missing PC conversion is resolved; Wii U execution remains unverified.
