# Scene skin binding capture — 2026-10-22 22:16

Capture: OctaneLiveInspector/Captures/ce_skinbinding_20261022_221603_341021015.jsonl. Saved analysis: ControllerState/skinbinding-221603-analysis.json. Analyzer: analyze_skin_binding_capture.py.

583 load binding events across31 objects,6 hand relationship snapshots, and a time-limit stop. Exactly one object has62 distinct influence slots:0x1EDC99B0. Load bindings occur around77.5s; hand snapshots follow at79.6–79.8s. No linked transform_matrix/dilation_matrix events were recorded despite77206/34118 raw site hits. That absence must not be treated as no animation.

## Exact numerical result

The6 hand snapshots contain matching input/output stamps and full known836-byte PC Elsa relationship hashes. Original PC RelationshipProcessor replay using serialized rig output initialization reproduces every output component exactly: maximum error0. Both left/right processors are covered at three captured stamps. This does not capture entry-state caches, prove all relationships, or establish renderer parity. The previous identity-initialized diagnostic was rejected because it omits authored output initialization; the accepted analyzer uses the same serialized initialization as the current decoder.

## Template/runtime boundary

Fresh bridge responses validate the session. Re-reading14 hand/finger slots from the62-slot object finds every slot still pointing to the captured node, but all sampled node stamps remain0. Producers resolve to the expected native Transform/Dilation-to-Matrix routines. Live snapshot: ControllerState/skinbinding-221603-live-hand-links.json. Bone names here remain file-order candidates until the runtime association is independently established.

Moving hand relationships in the capture are0x23346280(right) and0x23346108(left), distinct from the load-bound network around0x1EFC/0x1EFE. A candidate matrix node downstream of the moving right-index output has a nonzero stamp and nonidentity matrix. This establishes a concrete template/runtime distinction to investigate; it does not yet establish that either candidate is the final GPU palette. A bounded scan of0x23000000–0x23FFFFFF found no object with the same load-object vtable; readable coverage was only4063232bytes, so absence is limited to that scan and type assumption.

No pose, weight, mesh or decoder-motion changes were made. No new manual finger adjustments are justified by the capture.

## Next

Trace scene/runtime copying, data-node remapping or the runtime skinning consumer rather than repeating the same load-only capture. The existing logger observes Association::SkinInfluence loading at preferred0x4A60A8; it does not observe every runtime clone or GPU draw. Use the recorded moving relationship outputs and captured load table to identify the remapping boundary and then validate actual runtime influence slots. Current bridge pointers are session-specific and require revalidation.
