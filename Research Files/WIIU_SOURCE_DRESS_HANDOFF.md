# Wii U dress paths with shared native dynamics — 2026-10-24

## Launch

Relaunch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd. It selects the separate bin/WiiUDressAdapter build with the actual Wii U64-bone mesh. The cache now has61evaluated outputs and three explicit hair fallbacks. The previous57-output source-mesh bake is preserved. The standard PC viewer launch/build remains preserved.

## Source graph and parameter adaptation

The four outputs are UpperDress_Left, UpperDress_Right, dressLeftStart and dressRightStart. Their anchors are evaluated from the differing Wii U leg/hips routing through SourceLegEval, reusing PC numerical operations. Source Dilation orientation composition and typed Transform conversion branches were added without mutating PC graph globals.

Wii U chains552/553 map to the tested PC chain kernels550/551. Before reuse, DressStates compares all fields of both particles and ChainData against the corresponding mapped PC nodes, recursively including particle flags, mass, damping, natural frequency, drag, constraint lengths, bind-transform variants and container extents. Only serialization Header indices and top-level node identity are normalized. All six parameter records match under the existing1e-6numeric tolerance.

SourceDressEval uses the existing native ChainStates and Aim feedback. Dynamic positions come from the Wii U source anchors, container and constraint paths; source Aim outputs feed the retained orientation state. There is no stored-output fallback for an unsupported dynamic processor. Unadapted chains fail explicitly.

## Simulation fixture and validation

The schedule is120phase-zero warmup ticks followed by305chronological simulation ticks at approximately60Hz. Every second clip tick is saved, producing153render samples. Gravity is the established PC preview fixture [0,-9.8100004196167,0]; no capsule collision scene or Wii U actor scheduler is reconstructed.

All850chain-step checks pass. Maximum root error is0; maximum segment-length error4.400506250501479e-7. Every native last-frame stamp matches the expected chronological tick. The bake produces612finite nonsingular dress matrices. Merge validation confirms all previous57output matrices remain exactly unchanged.

Build has zero warnings/errors. WPF source-mesh smoke loads64bones,153samples,61source-driven/3fallback and skins all5419vertices successfully. The endpoint screenshot wiiu-dress-endpoint-smoke.png was inspected: the lower dress now hangs around the foot region instead of retaining the earlier rigid diagonal gap. This is a qualitative fixture improvement, not a live-game parity measurement. Standard PC viewer smoke and malformed-animation recovery/import checks also pass.

## Limits

Three hair outputs still use bind-relative parent fixtures. The dress has source-matched chain parameters and actual temporal state, but environment gravity/collision/activation remain explicit preview fixtures. Clipping and differences from the running game may persist. Matching PC PNGs are still used for preview textures; this step concerns source graph motion, not new Wii U texture decoding.

## Reproduce

From workspace root:
```
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_dress.py
python WiiUResearch/AnimationViewerResearch/merge_wiiu_dress_preview.py
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/WiiUDressAdapter --no-restore
OctaneCharacterViewer/bin/WiiUDressAdapter/OctaneCharacterViewer.exe --smoke-test --wiiu-adapter-smoke-test --wiiu-model
```

Next: inspect the new continuous dress motion, then adapt the remaining source hair chain and its differing hairStart connection with the same parameter/equivalence gates. Do not compensate by tuning bone angles.
