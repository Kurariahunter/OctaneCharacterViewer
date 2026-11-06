# Live PC dress dynamics capture: 2026-10-17 17:32

Source: F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures/octane_20261017_173236_1792272756642966600.json (matching supplied summary inspected). 240 samples,4upstream/IK context samples. This is actual new capture evidence; no native simulation replay was performed in this analysis.

The two previously connected updating candidates0x1e07fdd0/0x1e07fe74 have LastFrame tracking global time in240/240samples each. The two identity/template-shaped candidates do not update with the global clock. Structural labels in the raw JSON remain qualified; equal stamps do not guarantee atomicity.

## New measurements

- External-force input is consistently [0,-9.8100004196167,0] on both updating candidates (240/240samples each). This is the missing gravity-like input from the zero-force preview; it is measured, not a guessed tuning value.
- Captured dt spans0.0110000009..0.0170000009seconds. The prior offline clips used30Hz steps. Matched replay must use actual captured dt and native substep behavior.
- Capsule descriptor count is0for both updating candidates throughout this capture. Do not invent body capsules to explain this particular result. This does not establish that no collision mechanism exists elsewhere in the game.
- No detail-field read errors; changed read-window stamps in25left/30right samples. Exclude these from initial pair replay.
- After requiring unchanged stamps at both snapshots, global-frame delta1 and actor LastFrame delta1:61left and54right candidate pairs. These are replay candidates, not proof of perfectly atomic actor updates.
- Roots exactly match captured constraint inputs in all unchanged-stamp rows. Maximum segment length residual is3.82e-5(left)/3.50e-5(right) at world coordinates around y108; retain floating-point magnitude and non-atomic read limitations when choosing tolerances.
- Raw particle prefixes, velocity/last-target inputs, output states and cached orientation are present. First frame reset/event raw prefix is zero on both.

## Next

Start with the115candidate consecutive pairs. Reconstruct a native synthetic fixture from the first snapshot's numeric state, patch all pointers/type/frame metadata safely, and apply the next snapshot's dt, force, anchor/container and root constraint. Compare both output positions and state against the next captured snapshot, including previous-orientation feedback alternatives if update order is uncertain. Preserve the original capture. Only after a matched step should the file-derived idle preview enable the measured force path and a validated time-step schedule. No additional capture is requested yet.

Analysis JSON: live-dress-dynamics-20261017-analysis.json (pair indices and detailed initial state). Existing zero-force and reset-only previews remain unchanged.
