# PC captured dress-step replay and gravity preview — 2026-10-17

## Ready scene

Open Assets/DI3PCGravityDressPreview/Generated/Elsa_PC_GravityDress_Preview.unity and press Play. Left active idle, right passive. One-shot; stop/play restarts. Source rig, geometry, weights, materials, prior previews and original live capture are preserved.

The Unity clips are baked offline from original PC idle controls through the source skin graph and original native dress math. Unity is not invoking the emulated native solver at runtime. This remains an independent62-bone skin palette,31source-driven bones plus bind-offset fallbacks; no Humanoid retargeting, finger/facial decode or full game blending.

## Captured-step result

replay_pc_dress_capture.py reconstructs a synthetic native fixture for each selected pair from octane_20261017_173236_1792272756642966600.json. EXE/capture hashes are checked. Numeric particle/bind/flag/scalar fields, velocities, previous output positions, last target, previous cached scalar at processor+0x38 and prior orientation are initialized from snapshot A. Inputs for the next step (dt, force, chain data, full Transform anchor, Dilation container and root constraint) come from snapshot B. Frame/last-frame differ by1. Reset-event prefixes and capsule counts are zero. Unknown nonzero particle storage is rejected.

All headers, producers, type metadata, network pointers and cached references remain synthetic. The code never executes game pointers or writes into the process; it uses the hash-pinned executable in Unicorn. Only bounded numeric payload ranges are copied.

Selected pairs:61left+54right=115. Earlier handwritten total117 was an arithmetic mistake; the saved pair lists always contained these115pairs. All115are nonstatic (tip displacement >1e-6).

- Previous-orientation + strict type tags + full dispatch:115/115 exact numerical root positions, tip positions and velocity components.
- Current-orientation alternative: also exact on this dataset. These cases do NOT resolve orientation feedback timing universally.
- Permissive historical type fixture: also exact; strict Transform/Dilation fixtures are used for the new preview.
- Explicit staged native step: also exact, establishing agreement with full dispatch on this input state.
- Zero-force ablation:0/115 tips within1e-5. Median tip error0.0001538352, max0.0006809802; max velocity component error0.0443458557. Roots remain constrained. Thus measured gravity contributes materially to this captured update.

These are numerical equality results, not a claim of byte-for-byte signed-zero identity, universal loader reconstruction or all animation decoding. Non-atomic capture qualifications remain; the selected pairs nevertheless reproduce the observed next numeric state exactly.

## Gravity idle preview

ChainStates now optionally accepts an explicit force and strict type fixtures. Defaults remain zero force and the historical fixture, preserving earlier callers. Strict mode retains authored Transform particle bind payloads/kinds and gives the anchor/container the appropriate synthetic native type tags. Source drag fields remain source-derived.

The new preview applies measured force[0,-9.8100004196167,0]. It runs native physics at nominal60Hz (captured dt range11–17ms) while sampling original file controls at each physics tick, exports every second tick at30Hz, and holds the initial pose for120pre-roll ticks before export. This initial state and regular time schedule are explicit preview choices; they are not the exact captured walking performance or its variable timing.

No capsule scene is supplied, matching zero capsule counts on these captured chains. This does not establish absence of every collision mechanism elsewhere in the engine. All game layers, scene update order and seamless simulation looping remain outside scope. The dress can still retain authored flare/pose characteristics; no vertices or weights were tuned to hide them.

Gravity plus60Hz/pre-roll changes the two dress-bone orientations by roughly5–11degrees versus the older zero-force preview. This comparison changes several setup factors; the captured-step zero-force test above is the isolated force ablation.

## Validation

1248exported-timeline chain steps have correct advancing native frame stamps. Root error 0.0, maximum length error 6.863347462582325e-08. Another480pre-roll chain updates also pass the adapter's root/length checks. 1248ankle checks pass (source skin path, no manual foot correction), maximum endpoint error 5.729481366449266e-07. Source world matrices remain representable as TRS.

Unity exported127active/186passive poses,620bindings per clip. All sample matrices reconstruct within6.03497e-7(active)/1.046807e-6(passive); skin vertices stay finite. Saved Animator knee movement and flat palette references pass; six poses rendered using temporary CPU skinning/materials. Fresh saved scene retains original project materials. GUID references resolve. Source rig and old scenes were not edited. The preexisting120-frame moving-anchor/full-vs-staged harness still passes after extending the adapter.

## Files

Canonical: F:/DisneyInfinityPortalTest/ElsaSceneResearch.

- replay_pc_dress_capture.py / pc-captured-dress-step-replay.json.
- native_pc_chain_step.py, pc_skin_palette.py, bake_pc_gravity_dress.py.
- pc-gravity-dress-animation.json / pc-gravity-dress-validation.json.
- pc-gravity-vs-zero-comparison.json.
- pc-gravity-dress-unity.log / pc-gravity-dress-render.log.
- pc-gravity-dress-delivery-validation.json.

Next: extend exact capture replay across longer consecutive runs and compare the final live Aim/skin transforms, preserving source pose, scene forces and simulation state distinctions. This milestone validates an actual native dress update against game data; it is not a complete universal character animation reader.
