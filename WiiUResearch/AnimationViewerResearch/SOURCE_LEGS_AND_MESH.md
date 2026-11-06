# Wii U source legs and source mesh in shared viewer — 2026-10-24

## Launch

Run OctaneCharacterViewer/Launch_WiiU_Adapter.cmd again. It now chooses bin/WiiUNativeMeshAdapter with --wiiu-adapter --wiiu-model. The title says Wii U Elsa source mesh and the golden scope line says57evaluated outputs/7bind-relative fallbacks. There are153source-sampled poses over the same clip. The standard PC launch/build remains preserved.

## Source-specific leg adaptation

wiiu_leg_adapter.SourceLegEval dispatches only differing source dependencies. Verified-equivalent closures delegate to the unchanged PC DressEval/raw evaluator. This avoids replacing the Wii U foot graph with PC routing. Source-specific paths reuse original numerical helpers for inverse chains, typed composition, connections, relationship evaluation and the two-link solver. Existing PC graph globals are not replaced.

Differences handled include source hips inverse concatenation, ankle-group routing, separate ankle outputs, ball-to-ankle world concatenation, and toe relationships. Wii U relationship blocks39/40 are both580bytes and endian-convert to SHA-256ae9cb5c2424e7bca6ac0e2ead218bc0f5e542250b2fcb656c11edb8eda2f6b30. They differ from PC relationship data, so they are evaluated from their own source bytes with explicit cache fixtures, rather than declared equivalent.

The original-PC connection harness now accepts an optional translation-offset input. Its default None path remains unchanged.32finite rotated-input fixtures match native translation-offset addition; explicit zero offset matches the no-offset result. This describes the bounded Dilation connection inputs tested, not all connection variants or Wii U machine-code parity.

## Validation

Eight leg influences (knees, ankles, balls and toes on both sides) evaluate at153times:1,224finite world matrices.306endpoint checks pass with maximum error4.5958669523272323e-7. Unit-stretch cases compare against independent original-native forward kinematics. Stretched cases compare against the authored target, following the existing PC validation boundary. Native target residual in an un-stretched solver is not treated by itself as a decoder error.

The previous49-output continuous reference cache was regenerated after the optional-input harness change and its complete SHA-256 remained5b9d1fea6cd964e68a5aae4bb036b8a298134c7e2662f76a03a84c7cce31894c. The final64-bone bake preserves all49prior matrices exactly and includes all8source leg matrices exactly. Seven fallback local transforms remain constant to6.661338147750939e-16. Bind identity error is below2.3e-16.

Both actual-Wii-U-mesh WPF smoke and standard-PC WPF regression runs exit0. The Wii U run loads5419vertices,64bones,153samples,57source-driven/7fallback. PC animation import validation still loads its two test clips, rejects two malformed caches and retains the previous preview. Build has zero warnings/errors. Screenshots were inspected, but no live-game or full animation parity claim follows from these checks.

## Why load the actual Wii U mesh now

The PC reference mesh has62influences and cannot directly represent the two additional Wii U ankle-weight channels. The source mesh was therefore exported with the existing Wii U mesh reader, native palette remaps, normalized weights, UVs and all64inverse binds. Source OCT SHA-256fdf7c0e753e8ae34a5f68cd9322c5b711e8b8fd3a161da3d08dbb682857dea92. The viewer permits only the explicit verified PC62orWiiU64layouts and checks the selected animation model hash. It does not silently accept arbitrary meshes or palettes.

Matching PC preview PNGs are reused after checking the source pupil/head/body material-name order. This is not new Wii U texture decoding. The animation and skin weights now use the actual Wii U mesh.

The remaining7fallbacks are four dress and three hair outputs, using explicit bind-relative parent fixtures inherited from the reference hierarchy. They do not have source temporal dynamics yet. Automatic actor scheduling, scene collision, Wii U numerical execution, full blending and complete runtime parity remain outside this checkpoint. PC-only rebake/profile controls are disabled in the Wii U mesh window to prevent accidentally loading the wrong model bake.

## Reproduce

From workspace root:
```
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_legs.py
python WiiUResearch/AnimationViewerResearch/build_wiiu_mesh_animation.py
python WiiUResearch/AnimationViewerResearch/validate_wiiu_mesh_animation.py
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/WiiUNativeMeshAdapter --no-restore
OctaneCharacterViewer/bin/WiiUNativeMeshAdapter/OctaneCharacterViewer.exe --smoke-test --wiiu-adapter-smoke-test --wiiu-model
```

The optional merge_wiiu_leg_preview.py retains a55/62PCreference comparison cache. Use the64-bone source mesh build for the actual ankle influences. Next: visually compare lower-body motion, then adapt the dress/hair temporal paths without changing the validated upper-body matrices.
