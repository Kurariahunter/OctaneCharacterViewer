# Resolved neutral upper-dress controls

2026-10-16. Capture octane_20261016_234703_1792208823288579300.json.60samples, complete scan,zero failed chunks.

Verified container accessors resolve left slot110 to input0xbd54480 and right111 to0xbd54600. Each input Dilation is identity across60samples, and exactly numerically matches its blended output0x1e0722d8/0x1e072db0. Scalar factors remain1.

The missing table_weight_float_hex is NOT a failed read: controller+28 is0(null weight container). Original routine0x4e373a uses constant1 in this branch. Thus table weight is implicitly1, not unknown or zero. Native fixed-point priority grouping and all blend behavior are not generalized by this one-contributor test.

Source upper-dress controls565/605 are also neutral in both decoded idle libraries. No hidden non-neutral contributor or input/output mismatch was found for these controls in the captured state. This supports this part of the pipeline but cannot identify active/passive clip or explain their differing thigh-driven poses.

Do not request another identical neutral-control capture. Next useful target: thigh/reference IK inputs and/or a deliberately different visible stance, with runtime state evidence. Original capture, mesh, weights and previews preserved. No fix claimed.

Report resolved-blend-control-validation.json and script validate_resolved_controls.py in OctaneLiveInspector. Previous LIVE_BLEND_CONTRIBUTORS_HANDOFF.md remains historical; this checkpoint resolves its missing effective table-weight observation as the native implicit1 branch.
