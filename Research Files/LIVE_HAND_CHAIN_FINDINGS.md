# Same-capture hand scalar to relationship results — 2026-10-20

Capture: `ce_handchain_20261020_003251_90030046.jsonl`.

The event budget ended capture after 192 relationship records: 96 complete pairs, no rejected pairs, spanning approximately 125–1469 ms after arming. This is a short bounded capture, not ten seconds of movement. The stop record's scalar_final count is zero because scalar callbacks cache observations without writing independent events; 336 linked scalar observations are embedded in relationship snapshots.

Full relationship blob hashes identify file processors 165 and 171 (hands) and 173 and 175 (thumbs), with 24 calls each. Using exit inputs and entry output initialization, the original native relationship evaluator reproduced all 96 outputs with maximum component error **0.0**. Type widths, node identities, selector zero, full blob hashes and input cache freshness were checked by the native replay analyzer.

At relationship exit, all **336** input links match the previously observed scalar setter's exact node address, producer address, four payload bytes and node stamp. Both scalar and input observations have fresh metadata stamps. All scalar observations precede their relationship exit. Four negative fixtures separately corrupt payload, stamp, producer and time; each invalidates the altered link.

Values include small native floating-point variations: the first observed hand bends are -46.89997863769531 and thumbs -14.899992942810059. Do not replace these with hard-coded rounded constants or assume exact equality to values from earlier captures.

This joins actual final scalar writes to local hand/thumb relationship inputs and native replay outputs in one capture. It does not prove nested calls, unique actor identity, or equality of the final skin palette. The scalar observation has millisecond time and evaluation stamp, not a standalone scalar event sequence or thread identifier. Cached observations can be reused; unchanged bytes/stamps establish observed agreement, not an additional setter invocation for every relationship read.

Next: join these local Dilation output nodes to downstream world-transform inputs and skin matrix outputs in one bounded capture. Reuse previously verified native world/matrix operations, but require actual pointer/stamp/byte continuity rather than joining captures solely by bone name or time. Viewer remains unchanged; no hand offsets added.

Reports: `ControllerState/live-hand-chain-links.json`, `ControllerState/live-hand-chain-native-replay.json`, and `ControllerState/hand-chain-link-negative-validation.json`. Reproduce with `analyze_hand_chain_capture.py` and `analyze_relationship_pose_capture.py` (pass an explicit report path for the latter to preserve earlier reports).
