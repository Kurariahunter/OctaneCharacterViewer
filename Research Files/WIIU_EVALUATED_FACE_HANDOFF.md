# Evaluated facial fixture — 2026-10-24

The standalone preview now defaults to Evaluated face diagnostic. It adds three brows, jaw, two lip corners and upper/lower lip to the four previously evaluated eyelids. Each world-output ID is discovered from its source skin association and TransformToMatrix producer, not assigned by bone-name palette order.

Added bounded graph support reuses existing original-PC numerical helpers: TransformTransformWithDilation (0x004D7E90), TransformTransformWithTransform (0x004D82C0), two-input ConcatenateChainTransform (0x0057E240), and no-offset TransformTranslationOrientationScaleConnection (0x004D9F50). Transform control leaves now apply authored translation, rotor and scale channels; source Scale.w and Unscale remain retained. Unknown channels and unresolved Euler operands fail. These operations extend the PC-helper replay; this pass does not establish Wii U instruction equivalence for each operator.

The eight face outputs are evaluated at three source-control snapshots: 24 finite, nonsingular world/skin matrices with logged defaults and processors. Matrices are recovered through original-PC point transforms. Preview skinning replaces each evaluated influence's carried contribution exactly once, preserving weights. Head and selected hair influences remain carried at bind-relative offsets, and the body remains at bind pose. Other runtime layers and complete actor scheduling remain unproven.

The middle sample differs from the carried-head diagnostic by at most 0.00677913 source mesh units; start/end differences are below 0.0000006. These are movement differences, not game-parity error scores. All 2,939 vertices outside the selected head group remain unchanged. All 16 mode/frame script checks and focus/reset/orbit/zoom handlers pass. Visual confirmation remains pending; prior browser policy blocked local file inspection.

Rebuild from workspace root:
```
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_face_fixture.py
python WiiUResearch/AnimationViewerResearch/validate_eyelid_skin_binding.py
python WiiUResearch/AnimationViewerResearch/build_eyelid_diagnostic.py
node WiiUResearch/AnimationViewerResearch/EyelidDiagnostic/check-preview.cjs
```

Production viewer is unchanged. Earlier modes remain available for comparisons. Next: visually inspect this face sample before expanding the partial palette or introducing more sample times.
