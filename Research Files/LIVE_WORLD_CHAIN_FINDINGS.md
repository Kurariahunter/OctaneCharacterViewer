# Local finger to matrix continuity — 2026-10-20

Capture: `ce_worldchain_20261020_003610_90229843.jsonl`.

The event limit ended capture at 256 records, approximately 110–1375 ms after start. It includes 37 refreshed relationship snapshots and **73 complete ordered chains**, each containing a world Transform, world Dilation and packed Dilation-to-matrix conversion. Full relationship hashes identify the hand relationships. This covers the index/middle paths of both hands; thumbs and other fingers are outside the probe.

All **219 downstream native operations** replay exactly with maximum component error **0.0**, without rejected records. Strict continuity checks require identical predecessor node address, producer address, payload bytes and evaluation stamp at each handoff. Typed snapshots must also be fresh. All 73 chains have ordered relationship → world Transform → world Dilation → matrix event sequences. A negative fixture changes one finite input payload while retaining its node and stamp; the continuity analyzer rejects it as changed since its predecessor.

These observations close the previously separate local-output-to-world-to-second-joint-matrix boundaries within one bounded capture. They do not show an uninterrupted clip-file-to-renderer evaluation, nor prove that the renderer consumes these particular matrices. Relationship computation itself was validated in the separate preceding hand-chain capture. No unique player actor or thread identity is established here.

Next check the actual viewer's composed pose and palette routing against these captured native values, starting with the same local and parent inputs. Retain native floating-point values and quaternion norm behavior. Do not introduce manual finger offsets to compensate for a graph or palette mismatch. Renderer bone-index/palette association and bind-space application remain separate checks if math agrees.

Reports: `ControllerState/live-world-chain-analysis.json` and `ControllerState/world-chain-continuity-audit.json`. Reproduce native and strict-link checks with `analyze_finger_world_capture.py`, using an explicit output path to preserve earlier reports. Viewer code is unchanged.
