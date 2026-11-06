# PC Elsa directional full palette — 2026-10-22

New opt-in evaluated previews:

* `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-runrf-full-palette.json` — diagonal right.
* `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-runr-full-palette.json` — sideways right.

Both use the existing hash-verified supported PC Elsa rig and class_girl run profiles, with62/62 palette bones evaluated and no bind-offset palette fallbacks. Each has0.6000000238418579s source duration,37 simulation frames and19 saved samples. These are the existing explicit direction profiles, not a reconstructed runtime direction selector.

## Validation

Fresh partial and full bakes preserve the same native main/upper/lean composition. Across every saved sample, only the16 newly enabled face/lid/eye/forearm paths change. All previously evaluated body, finger, hair and dress matrices are exactly unchanged. This step does not fix the known running index finger.

Both bakes pass endpoint, native matrix, shear and dress invariants. Diagonal maximum endpoint error6.314408855482093e-6, sideways3.6471474246723403e-6. Both maximum native matrix component errors2.384185791015625e-7. Maximum differences from fallback baselines0.05767186626542148 and0.057654966573542854 are matrix-component differences, not visual error scores.

Reproduce the checks with `audit_full_palette_walk.py --motion runrf` and `--motion runr`. Reports: NativePreviews/full-palette-runrf-audit.json and full-palette-runr-audit.json, plus adjacent bake `.validation.json` files. Same-run baselines are native-runrf-coverage-baseline.json and native-runr-coverage-baseline.json.

The Full palette checkbox in the rebuilt viewer now supports these profiles as well as the previously tested idle and forward walk/run profiles. Use Launch_Viewer.cmd; the option remains unchecked initially. Only catalogued source hashes are accepted. Build passes with zero warnings/errors.

The hidden end-to-end viewer check with --selected-native-smoke-test --diagonal-run-smoke-test --full-palette exits0 and records grl_bm_runrf_NativePreview,19 samples,62 source-driven /0 fallback. This verifies the checkbox/backend/load path, not game visual parity.

New directional full-palette visuals still need user confirmation. Numerical coverage is distinct from full game parity, arbitrary character compatibility, channel-default policy, automatic scheduling and actor/physics context.

Next: use these complete palettes to compare actual game poses at matched phases, focusing on the remaining finger discrepancy and secondary-motion context rather than further bind-offset fallback removal.
