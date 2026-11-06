# Standalone viewer checkpoint — 2026-10-18

Launch F:/DisneyInfinityPortalTest/OctaneCharacterViewer/Launch_Viewer.cmd.

First independent C# WPF viewer is built and tested. It skins the original verified PC Elsa mesh using existing cached native-evaluated run/braid poses, without Unity or the game running. Asynchronous source re-evaluation launches the original Python/native-emulation pipeline, reloads the pose cache on success and writes backend-last-run.log. This is not complete engine execution or a generic file loader. Original mesh extraction currently uses a one-time Unity export bridge; replacing it is future work.

Static inventory for all62 skin outputs:707 data nodes,421 processors,47 processor types. Current evaluated palette46 source-driven,16 fallback. Static reachability is not executed coverage. Full scheduler/layer state, actor identity, collisions, external forces and additional processor paths remain unresolved.

Validation: .NET10 WPF build zero warnings/errors; headless/offscreen UI smoke renders texture and mesh;73 pose samples finite and moving; source-native backend refresh succeeds; independent C# vs numpy skinning compares3 complete frames x5419 vertices, maximum coordinate difference4.44e-16. Viewport screenshot checked and camera framing repaired. Interactive orbit/zoom/play controls still need user confirmation. No timing or complete game parity claim.

See DEPENDENCY_INVENTORY.md for next capture requirements. No new Cheat Engine inspection is needed to run this prototype. A later synchronized capture must identify the Elsa actor and associate clip/layer/time state, final palette and braid548 inputs/outputs in the same frames. Do not substitute unidentified controller logs.

User hand settings from screenshot130950 recorded separately in hand-visual-checkpoint.json; manual offsets are not applied to raw standalone playback.


## Follow-up: normalized parameter verified

See PC_EXE_NORMALIZED_PARAMETER_HANDOFF.md. The prior expression-backed terminology is narrowed: native 0x59d3c0 is a normalized scalar accessor, with getter/delegation, setter and clip-time remap tests now passing. Binding actual actor parameters and resolved masks remains unverified; existing previews are unchanged.
