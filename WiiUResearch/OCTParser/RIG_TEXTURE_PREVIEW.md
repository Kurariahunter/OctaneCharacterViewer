# Rig and texture preview controls — 2026-10-23

Build: RigTextureBuild/AssetWiiUdio.exe. Full application Release build:
0 errors; 17 existing nullable/GX2 analyzer warnings.

- Show rig / scene nodes overlay; Rig only mode; node names list.
- Actual SceneTreeNodePool positions composed through ParentNodeReferences.
- Recorded parent links only; no invented skeleton links. Cycles, missing parents,
  and multiple-parent instances fail explicitly.
- Grimm pieces contains six scene nodes (root plus five rigid pieces), not a
  full character skeleton. A full skeletal viewer still needs the character's
  skeletal data and verified joint associations; these markers are not a substitute.
- Archive mesh extraction includes bundled TBODY/MTB files. Existing native
  GX2 decoder produces bitmap images; per-material dropdowns apply chosen
  color textures immediately. Assignment is manual, shared across primitives
  with the same material reference. Normal maps must not be chosen as color maps.
- No automatic Wii U shader sampler mapping, normal-map shading, skinning,
  or external texture archive lookup is claimed.

PreviewCheck exercises actual WPF window construction, all four Grimm GX2
decodes, rig-only rendering, material selector events, and mesh+rig rendering.
rig-ui-check.png was visually inspected. Texture render test assigns a test
BC1 image through the controls; it does not validate the game's material map.
Original preview/archive source backed up in BeforeRigPreview.
