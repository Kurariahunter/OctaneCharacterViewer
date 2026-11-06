# Octane Character Viewer — first standalone prototype

Run Launch_Viewer.cmd. The executable is in bin/Release/net10.0-windows/OctaneCharacterViewer.exe. Uses the installed .NET10 Windows Desktop runtime. This prototype is configured for F:/DisneyInfinityPortalTest and the verified PC Elsa source assets; it is not portable yet.

## What works

- C# WPF window with textured original PC mesh, original weights and inverse binds; CPU skinning independent of Unity.
- Play/pause/restart, frame stepping, timeline, orbit and zoom.
- Existing native-evaluated PC Elsa run/braid pose cache (73 samples / 2.4seconds). All manual Unity finger diagnostic offsets are absent.
- Re-evaluate source launches the existing Python/native-emulation backend asynchronously, then reloads validated poses. Closing the window terminates its own running backend process.
- Research inventory opens DEPENDENCY_INVENTORY.md, with machine-readable dependency-inventory.json beside it.

## Scope boundaries

This is NOT the complete engine, its original renderer, or continuous live game-code execution inside the C# rendering loop. Playback skins sampled native-evaluated poses. Scrubbing chooses the closest saved pose; it does not simulate state backwards. Re-evaluation still takes the full offline bake time. Compatible evaluated animation files can now be opened and their clips selected; native OCT channel inspection is available, but no generic character/full native animation player yet; unsupported paths fail explicitly in the existing bounded evaluator.

Initial mesh/texture extraction used a one-time Unity export bridge from the verified generated prefab. The original vertices, weights, inverse binds and textures were exported without baking animation. Playback and native evaluation refresh do not need Unity or the game running. Replacing that bridge with a validated direct binary mesh reader is a later milestone.

The backend uses original executable routines through emulation plus a reconstructed Python graph dispatcher and explicit fixture state. Native numerical checks do not prove full game blending or actor parity. Full source-layer scheduling, actor runtime inputs, collisions, additional processors and16 fallback palette bones remain unresolved.

## Backend dependencies

Uses bundled Python at C:/Users/Kurar/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe, local evaluator scripts in ElsaSceneResearch, their configured analysis dependencies and the installed game EXE/source assets. No new Python packages were installed. Backend log: backend-last-run.log.

## Research next

Read DEPENDENCY_INVENTORY.md. No Cheat Engine action is needed to use this first viewer. Next capture design should identify Elsa's actor and synchronize final bone palettes with active clip times/layers and braid548 state. We will specify verified hook locations before asking for a new capture; avoid another broad unidentified-controller dump.

## Development and checks

Build: dotnet build OctaneCharacterViewer.csproj -c Release
Smoke: OctaneCharacterViewer.exe --smoke-test
Backend smoke: OctaneCharacterViewer.exe --smoke-test --backend-smoke-test

Smoke checks all cached poses for finite moving skinning and saves viewer-smoke.png, smoke-test.json and three frames of skinning-reference-points.json for independent comparison. UI mouse interaction still requires user confirmation.

## Native clip inspection and animation file loading

See NATIVE_CLIP_LOADING_HANDOFF.md. The two file controls deliberately distinguish decoded native channels from evaluated skin-palette playback.

## Selected native clip evaluation

**Preview native clip (.oct)** now evaluates the four hash-identified PC Elsa idle/forward locomotion profiles into a new skin palette and loads it automatically. See SELECTED_NATIVE_PREVIEW_HANDOFF.md for use, tests, fixtures and remaining unsupported behavior. This is a partial source graph evaluator, not full game-runtime parity.
