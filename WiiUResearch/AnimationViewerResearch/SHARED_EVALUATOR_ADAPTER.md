# Wii U adapter into the existing native viewer — 2026-10-24

This replaces the separate-preview-first approach with reuse of the established PC evaluation and rendering pipeline. It is an initial adapter/reference-rig test, not a completed Wii U animation loader.

## Verified mapping and reuse

- Wii U Elsa has 877 data nodes; 870 have unique shared authored paths into the verified PC model's 879 nodes.
- All 870 mapped stored Data slots match within 1e-6 (including absent Data). This does not assert all runtime/metadata fields match.
- 847 mapped node producer signatures match after serialization-only Header indices are excluded. Signatures compare type, output attribute, all referenced authored paths, and remaining processor configuration. These are node signatures, not 847 distinct processors.
- Six mapped relationship blocks (34,35,36,37,38,41) are byte-identical to PC data after field-aware endian conversion. Toe relationship blocks39/40 have different paths and remain outside this equivalence claim.
- 84 source leaf-control rows per snapshot map into PC canonical IDs. Two computed-output records are skipped explicitly, matching the existing PC apply policy. Raw Euler controls retain the already-validated quaternion conversion.
- The unchanged existing DressEval/raw/finger implementations evaluate 49 of 64 Wii U output dependency closures at three times. Each admitted closure requires matching type, stored Data, producer signatures and any relationship bytes. Dynamics paths are explicitly excluded.
- 23 outputs overlap the narrow independent Wii U graph replay. Maximum matrix component difference is 5.841255187988281e-6, below the explicit 1e-5 crosscheck bound. This comparison does not establish full native Wii U numerical execution.

## Working native viewer test

Launch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd. It uses a separate bin/WiiUAdapterPreview build. The standard Launch_Viewer.cmd still chooses the established PC build.

The new viewer button is Wii U controls / PC reference. It loads wiiu-controls-pc-reference-viewer.json through the existing validated animation-cache loader. The reference file uses the PC mesh's62-bone layout:49 evaluated outputs and13 explicitly bind-relative fallback outputs. Wii U has two additional ankle influences, so49/62 in this reference test does not mean49/64 is a complete Wii U mesh bake. No fallback is labeled source-evaluated.

The loaded clip is WiiU_Elsa_Controls_PC_Reference_49_of_62. It contains three discrete snapshots at0,2.5333333015441895,5.066666603088379seconds. Playing/scrubbing selects cached poses; this is not continuous source-clip decoding. The golden scope label states the reference mesh and fallback counts.

Build passes with zero warnings/errors. Hidden WPF smoke run --smoke-test --wiiu-adapter-smoke-test exits0, loads all three62-matrix samples, skins5419vertices and reports49source-driven/13fallback. Existing invalid-animation import/recovery checks also pass. The adapter screenshot was inspected. A finite moving image is not a live-game parity test; fallback legs/dress/hair still need source-specific adaptation.

## Remaining differences

Fifteen Wii U output paths remain blocked from direct reuse: toes/balls/ankles/knees, upper dress/dress starts, and three hair outputs. Mismatches include actual foot/ankle graph structure, hips routing, hairStart connection and temporal dynamics. The adapter refuses to substitute the PC graph for these paths. Do not loosen these gates to make a full-palette label pass.

Next: adapt those differing source paths within the shared evaluator interface, recover both Wii U ankle outputs, and replace the three approximate control snapshots with continuous native clip sampling. Then feed the Wii U64-bone mesh through the same renderer. Preserve existing run/profile regressions.

## Reproduce

From workspace root:
```
python WiiUResearch/AnimationViewerResearch/wiiu_pc_graph_adapter.py
python WiiUResearch/AnimationViewerResearch/reuse_pc_evaluator.py
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/WiiUAdapterPreview --no-restore
OctaneCharacterViewer/bin/WiiUAdapterPreview/OctaneCharacterViewer.exe --smoke-test --wiiu-adapter-smoke-test
```

Evidence: wiiu-pc-graph-comparison.json, wiiu-controls-pc-canonical.json, pc-evaluator-wiiu-adapter-check.json, wiiu-controls-pc-reference-viewer.json and OctaneCharacterViewer/wiiu-adapter-viewer-smoke.json. Existing PC profile restrictions remain in place; Wii U clips are not silently added to the verified PC catalog.
