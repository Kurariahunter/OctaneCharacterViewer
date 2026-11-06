# Selected native clip to rig preview — 2026-10-18

## Use

Launch Launch_Viewer.cmd and click **Preview native clip (.oct)**. Select one of the four exact PC source clips listed in native-preview-profiles.json:

- elsa_bm_idle_active.oct
- elsa_bm_idle_passive.oct
- grl_bm_walkf.oct
- grl_bm_runf.oct

The source bytes, not the filename, identify the profile. Copied identical extracted clips work. Upper-body additive clips alone and unrecognized files are rejected with the old preview retained. Native inspection remains available for other clips.

Evaluation runs in a background process with progress in the WPF window. When it succeeds, the new palette is validated and loaded automatically. Play/pause, stepping, orbit and scrubbing operate on these newly generated samples. Closing the viewer terminates its own backend process. Existing caches are not overwritten. Generated files are under NativePreviews, with a validation file and metadata for each. native-preview-last.log records the latest UI evaluation.

**Re-evaluate source** remains the original fixed run/braid regression bake. **Preview native clip** is the selected-source path.

## Evaluation pipeline

Selected OCT -> strict tuple/ClipDataBlock decoder -> existing original scalar-curve and Euler routines -> mapped PC Elsa control inputs -> partial reconstructed rig dispatcher invoking native processors -> chronological dress/braid state -> 62 named world skin matrices -> reflect to viewer coordinates -> CPU skin original mesh and weights.

46 source-driven skin outputs; 16 fallback bones inherit documented bind offsets. No Mixamo, Humanoid retargeting, new weights, or manual visual hand/finger corrections.

The implementation reuses the established PC run/braid evaluator. Locomotion initializes absent controls from passive idle phase zero, applies matching upper-body channels, and for run applies the source static lean through the native additive buffer routine at fixture weight 1. Two source Transform controls permit the previously verified nonuniform scale only in the run profile. Other profiles use the existing identity-scale checks.

Dynamics use 120 reset-pose warmup ticks, approximately 60 Hz stepping, 30 Hz sample export, measured gravity fixture [0,-9.8100004196167,0] and no capsule collision scene. CLI supports 1–4 cycles, UI requests one. Single-cycle previews include the authored end; multicycle run regression retains the prior seam semantics. No seamless-loop claim.

Every output records selected and companion hashes, source node coverage, fallback hierarchy, unmapped ports, clip channels targeting computed outputs, unhandled opcodes, and fixture assumptions. Computed-output channels (run baseline nodes 364/382) are explicitly skipped by the existing leaf-only control adapter; no complete clip-buffer/graph blend claim is made.

## Verification

- Actual native file evaluation succeeded for both idles, forward walk, and forward run. Each sample contains 62 finite matrices and passes positive scale / shear / leg endpoint checks and native matrix-versus-point comparison.
- Four-cycle forward run matches the previous 73-sample run/braid checkpoint exactly across all 62 matrices (max difference 0).
- Four exact source profiles accepted; additive-only clip, non-OCT and zero cycle request rejected.
- C# Release build: zero warnings/errors.
- Offscreen end-to-end WPF selected-native smoke test: selected source .oct -> Python rig evaluation -> output palette loaded -> 19 new samples displayed; pass, 46/16 coverage.
- Existing multi-clip import, invalid file retention, and normal playback smoke checks still pass. Existing CPU skinning reference comparison remains 4.44e-16 maximum coordinate difference (3 x 5419 vertices).

See selected-native-validation.json, selected-native-preview-smoke.json, NativePreviews/*.validation.json and logs.

## Remaining research

This is not a full Octane engine or an arbitrary-character/native-clip player. It still uses the one-time Unity mesh bridge and existing generated prefab hierarchy as offline research dependencies. Idle/walk now reuse the expanded finger/braid evaluator; source-processor invariants and finite motion are verified, but in-game visual parity for these new combinations is not. Facial channels, missing output paths, masks, effective runtime weights, expression weights, clip timing/scheduler, actor motion and collisions remain incomplete.

No new live capture is needed to use this step. The next fidelity milestone remains identified, synchronized actor clip/layer/time + final palette capture and resolution of currently skipped channels and source filters. Do not use guessed visual corrections to conceal discrepancies.
