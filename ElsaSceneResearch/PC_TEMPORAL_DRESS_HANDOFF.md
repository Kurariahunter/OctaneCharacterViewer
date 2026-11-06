# PC temporal dress update — 2026-10-17

## Preview

Open Assets/DI3PCTemporalDressPreview/Generated/Elsa_PC_TemporalDress_Preview.unity and press Play. Left active, right passive. Clips play once; stop/play restarts. The original rig, source mesh/materials and previous reset-based preview are preserved. This is the same independent 62-bone palette (31 source-driven), with temporal native lower-dress chains replacing per-sample resets.

## Implemented

native_pc_chain_step.ChainStates owns separate persistent native-memory snapshots per side and per clip. It uses source PC processors550/551, original DynamicChain full dispatch0x4ae360, reset0x4acad0 and step0x4acdb0. Each clip starts reset; subsequent frames restore particle positions/velocities/last target/frame state and apply the new anchor, container, source root constraint and delta time. Previous local Aim orientation is fed back through the cached ^.Orientation reference. Sampling must be chronological. Invalid time, unsupported chain IDs, nonuniform anchors and invalid feedback are rejected.

The source PC DragCoefficient is written to particle+0x98 for this bounded adapter; all five particle scalar float32 fields and flags match the two previously connected PC chains across60 captured samples (240 particle matches). This corroborates the bounded field mapping, not exact live-motion replay or universal loader equivalence. No value is hard-coded to0.5 globally. Other particle fields retain source values and the same reset fixture representation.

The native frame stamp advances correctly on all626 actual idle chain evaluations. Full native dispatch and explicit staged reset/step produce exactly identical positions for a120-frame controlled moving-anchor test. Measured maximum tip lag is0.0040072519 source units. That fixture proves stateful response; it is separate from the original idle recordings.

## Actual idle result and limits

The original idle inputs produce only a small difference from reset each frame: maximum dress world matrix component difference0.0007411242, approximately0.053 degrees rotation. Passive right dress remains numerically identical to reset in this bounded setup. This does not solve the visibly flared passive shape or establish all original game cloth behavior.

External force is explicitly zero and capsule scene linkage is absent. The existing capture identifies the external-force input address but does not include its vector payload in upstream nodes; it cannot justify inventing gravity/force values. Container constraints, source spring settings and source root targets remain native. Original scene loader, full update order, exact game clip/layer identity, collision response and seamless loop-state matching are not established.

The preview is one-shot to avoid presenting a reset at the loop boundary as verified continuous simulation. The skin/foot attachment improvements from the prior preview remain. Fingers, facial motion and full game blending remain outside scope.

## Validation

- 626 ankle checks, maximum endpoint error 4.36347579401143e-07.
- 626 dress chain checks, maximum root error 0.0, maximum segment-length error 6.376270639263382e-08.
- 626 native frame stamps match their sampled frames.
- 100%-exact full-vs-staged positions in the120-frame moving fixture, with feedback.
- 240 captured particle scalar/flag signatures match source PC values.
- 3 invalid input/time cases rejected.
- Unity active127/passive186 samples: matrix reconstruction max6.03497e-7 /1.046807e-6; finite skins;620 bindings per clip.
- Saved Animator knee motion measured0.5352216/1.786134 degrees; six still poses checked with CPU skinning and original palette bone references. No shin gap in checked views.
- Delivery GUID references resolve; original source geometry/material references preserved.

## Files and reproduction

Canonical research directory: F:/DisneyInfinityPortalTest/ElsaSceneResearch.

- native_pc_chain_step.py — persistent frame update adapter.
- evaluate_pc_temporal_dress.py — original source graph with previous Aim feedback.
- bake_pc_temporal_dress.py — original PC idle controls -> native temporal skin world poses.
- validate_pc_temporal_dress.py — moving-anchor equivalence, scalar signature and boundary checks.
- pc-temporal-dress-animation.json, pc-temporal-dress-validation.json.
- pc-temporal-dress-harness-validation.json, pc-temporal-vs-reset-comparison.json.
- pc-temporal-dress-unity.log, pc-temporal-dress-render.log, pc-temporal-dress-delivery-validation.json.

Next evidence: capture the connected PC chains' frame delta, external-force vector, reset/event state, capsule/container linkage and previous/current particle/orientation states during visibly moving game playback. Reproduce a consecutive runtime step before claiming game-equivalent fabric behavior. Do not add arbitrary gravity, exaggerated sway or skin changes to make the research preview look more dynamic.
