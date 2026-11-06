# Finger input/output diagnostics

Native preview reports now include finger_diagnostics at start, middle and end. Each of four relationship processors records the actual scalar inputs after current preview composition, node/path, override/default provenance, per-source application stages, relationship block hash and raw native output quaternion/translation/scale. No manual offsets or pose corrections were added.

Run audit: NativePreviews/native-default-run-finger-audit.json. All existing bake invariants pass. Comparing the entire clips payload to native-default-run-test.json gives exact equality for all 19 samples. Summary: finger-diagnostic-validation.json. This is an instrumentation regression check, not proof that the hand pose matches the game.

## Findings

At frames 0, 18 and 36, both hands use Index1/Index2/Middle1/Middle2 = -46.900001525878906, spreads zero, and both Thumb2 inputs = -14.899999618530273. Every input is a composed override, not a fallback rig default. The upper-body run source supplies these values after the passive-idle base at phase zero. Main forward-run source does not appear as an applied stage for these particular inputs.

Examples of the overwritten base: left Index1 -52.35881423950195, right Index1 -2.299999952316284, left Thumb2 -16.399999618530273, right Thumb2 -12.899999618530273. Current upper-body source application replaces both sides with the values above. Native relationship output quaternion norms differ from 1 by at most about 1e-7 at sampled frames; malformed quaternion length is not apparent here. Correct unit length does not prove correct rotation axes, parent transforms, authored composition or active game inputs.

`pc_graph_controls.apply` starts each applied record from serialized rig fields and replaces the node override. Diagnostics make that existing behavior explicit. A filename containing _add does not establish scalar additive arithmetic; do not change it merely on that basis. Missing live layer weights or downstream hierarchy differences remain candidates.

## Next

Compare these exact scalar ports (left Index1 483, right Index1 510, thumbs 805/812) and relationship output transforms against game-state data or verified native layer composition. Determine whether the discrepancy enters before relationship evaluation, during local/world composition, or skinning. Preserve the no-offset native baseline while investigating. The current report is sufficient for the next static/source audit; no additional broad gameplay recording is required yet.

New previews automatically include the diagnostic snapshots. Existing evaluated caches stay unchanged. Idle and walk diagnostics can be produced through the same Preview action, but the detailed findings above apply only to the tested forward-run profile.
