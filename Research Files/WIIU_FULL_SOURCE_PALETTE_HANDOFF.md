# Supported Wii U Elsa idle: complete64-output palette — 2026-10-24

## Launch and scope

Relaunch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd. It now selects the separate bin/WiiUFullPalette build, actual Wii U mesh and wiiu-source-mesh-animation-full.json. The clip is WiiU_Elsa_SourceMesh_FullPalette_64_of_64. The scope line reports64source-driven/0fallback and153source-sampled poses.

This completes the skin-output palette for the one supported Elsa specific-idle profile. It does not complete the engine, actor scheduler, arbitrary clip loader, platform CPU equivalence or live game parity. Physics activation, gravity and collision remain explicitly bounded fixtures. All earlier partial caches/builds are preserved; the standard PC launch remains preserved.

## Final hair adaptation

The source hair outputs are hairStart, hair01 and hair02. Source hairStart's orientation connection has the same typed inputs/offset path as PC but a different serialized NetworkBufferOffset (256versus264). It is evaluated through explicit source references and the original numerical connection helper; the generic graph-equivalence gate was not weakened to ignore arbitrary buffer fields.

Wii U DynamicChain550 maps to the tested PC braid kernel548. Its two particles and ChainData match the mapped PC parameter records recursively under1e-6tolerance, including flags, natural frequency, damping, drag, bind-transform variants, lengths and container extents. DressStates now validates all three chain groups (nine parameter records); hair evidence reports its own three records separately.

Source hair Aim669 uses the same retained local orientation feedback mechanism as the established PC BraidEval. Source routing provides anchor, container, constraint, alignment and up vectors. Native chain positions and feedback persist chronologically. Unsupported chains still fail explicitly; no PC graph globals are replaced and no empirical angles are applied.

## Simulation and regression

Hair uses120phase-zero warmup ticks plus305clip ticks at about60Hz, saving every second clip tick to153poses. The established PC gravity fixture is used, with no capsule collision scene. All425hair chain checks pass: maximum root error0, maximum segment-length error3.444871023994267e-7. The bake produces459finite hair matrices.

The final merge replaces only the three previous hair fallbacks. Every prior61output matrix remains exactly unchanged. All64source_skin_nodes match the file's explicit SkinInfluence->Matrix4x4 producer-input associations. The full regression checks every64-matrix palette, finite values, positive nonsingular basis determinants, homogeneous rows, exact hair matrix inclusion and chronological native frame stamps. No bind-relative fallback outputs remain in this cache.

Build: zero warnings/errors. Native WPF smoke loads64bones,5419vertices,153poses and64source-driven/0fallback. Endpoint screenshot wiiu-full-palette-smoke.png was inspected. Standard PC viewer smoke and its two malformed-cache rejection/recovery checks also pass. These validate implementation consistency, not a1:1game comparison.

Preview PNGs still come from the matching PC material references; this is not a new Wii U texture decoder. Remaining practical gaps include environment collision, actor activation/layers, broad clip support and runtime parity comparisons. Full palette coverage is independent of those gaps.

## Reproduce

From workspace root:
```
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_hair.py
python WiiUResearch/AnimationViewerResearch/merge_wiiu_full_palette.py
python WiiUResearch/AnimationViewerResearch/validate_wiiu_full_palette.py
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/WiiUFullPalette --no-restore
OctaneCharacterViewer/bin/WiiUFullPalette/OctaneCharacterViewer.exe --smoke-test --wiiu-adapter-smoke-test --wiiu-model
```

Prerequisites are the existing shared49-output bake, source8-output legs bake, source4-output dress bake and64-bone mesh export, preserved in earlier handoffs. Next: inspect the continuous hair/dress motion, then generalize the supported clip adapter with new source profiles and keep this64-output idle as a regression baseline.
