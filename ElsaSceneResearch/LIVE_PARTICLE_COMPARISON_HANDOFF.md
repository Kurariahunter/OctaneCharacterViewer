# Captured particle scalar comparison

2026-10-16. Source live capture octane_20261016_224545_1792205145222838300.json.

## Result

Original native DynamicChain dispatch with particle+0x98=1 versus0.5 produces EXACTLY IDENTICAL particle positions and lower-dress skin matrices across active127 and passive186 sampled frames. A120-frame moving-anchor fixture with original source flags also produces identical positions. Existing value1 bake reproduced exactly. Thus the captured discrepancy is real, but is not a bulge fix in these bounded source fixtures. No preview, skin weights or production importer changed.

Native integration read0x4a21ef is behind a ConfigFlags bit0 check. Tip flags6 do not take that branch; root flags5 participate but are root-constrained in these tests. A separate original-code arithmetic block0x4a21ef..0x4a222b with explicit nonzero inputs responds exactly: value1 yields[2,3,1];0.5 yields[1,1.5,0.5]. This verifies arithmetic sensitivity, not a universal parameter name or complete simulation behavior. An initial synthetic tip-flag change required additional fixture inputs and faulted; that incomplete configuration was discarded rather than used as evidence.

Source constructor0x48e9f0 initializes scalar94/98/9c/a0 to1; loader0x49ffdd directs property hash0x5b9e19db to98 through0x481030. That scalar property reader leaves the destination unchanged on absence/type mismatch. Why the captured game objects hold0.5 is not yet established; it may involve a different loaded asset or later runtime setup. Do not hard-code0.5 globally without tracing that write.

## Source signature associations

Exact float32 comparisons of flags, inverse mass/damping/frequency/length, relative targets (including tiny signed components), and chain-data parameters give one Elsa-source match for each captured chain:

| World-space candidate | Source processor | Source anchor | Configuration |
|---|---|---|---|
|0x1e07fd08|583|408|Hair chain|
|0x1e07fdd0|585|660|Left dress|
|0x1e07fe74|587|668|Right dress|

Identity/zero-output candidates0x1dcc5a8c,0x1dcc5b54,0x1dcc5bf8 match the same three configurations respectively. These unique matches within Elsa's source support the correspondence; they do not prove runtime character ownership or template versus instance lifetime. Addresses are valid only for the captured process state.

## Next live capture prepared

Capture Running Game.cmd now provides5seconds to return focus to the game, then scans and records60samples over about15seconds. Adds chain LastFrame/reset, first cached Orientation quaternion/reference, and node-header bytes. The shared frame advanced in the initial capture, but anchor and dress outputs were static; do not assume that proves character evaluation advanced. Keep Elsa visibly animating in the foreground during the next capture. No new live run is claimed from this session; administrator read access remains necessary.

## Files

compare_live_particle_scalar.py -> slot98-native-comparison.json and two independent native-dress-slot98_1/slot98_05-samples.json files. Original native-knee-dynamic-dress-samples.json preserved.
match_live_chain_signatures.py -> OctaneLiveInspector/live-source-chain-signatures.json.
Next evidence target: LastFrame plus cached Orientation and live input state during actual animation, then follow the instance anchors upstream to upper-dress objects.
