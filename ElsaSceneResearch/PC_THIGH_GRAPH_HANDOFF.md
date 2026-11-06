# PC thigh-to-dress graph adapter

Implemented native_pc_lean_ik.py as a reusable offline wrapper for the hash-pinned installed-PC 8/3 solver. Refactored validate_pc_lean_replay.py to use it; replay results retained (connected pair: exact 60/60 and 56/60).

Implemented evaluate_pc_thigh_graph.py and generated pc-thigh-graph-validation.json. The adapter identifies source side from all three exact float32 initial-position signatures, requires a unique match, and requires the actual runtime output alias at a captured dress upstream boundary. It keeps PC assets separate from the old 13/4 model family.

Source paths established:
- PC processor 405 -> StartOrientation 404 -> UnitRotor connection 553 -> node 615 -> orientation-only Dilation compose 366 -> node 610. Runtime solver 0x1e07e324, rotor output 0x1e06ec84, connection output 0x1e0734a4, aggregate 0x1e073300.
- PC processor 411 -> StartOrientation 432 -> UnitRotor connection 552 -> node 609 -> orientation-only Dilation compose 361 -> node 604. Runtime solver 0x1e07e434, rotor output 0x1e06f740, connection output 0x1e0732bc, aggregate 0x1e073118.

The source bridge emits StartOrientation, MidOrientation, Scale and the two proven connection/aggregate paths as source-indexed per-sample values. Compose preserves authored Translation and uniform Scale. Original engine basis is retained; these values are not Unity-local curves.

Validation across 60 frames per side:
- Source/runtimes uniquely identified from initial geometry; 120 mapped sample rows.
- Same-graph solver output to rotor connection: exact in all 120 rows.
- Same-graph orientation plus source bind translation/scale to composed Dilation: processor 411 path exact throughout; processor 405 path maximum component discrepancy 0.0001832395792.
- Independently sampled solver pass vs upstream graph differ in 36/60 frames for each side. Max direct native-to-graph quaternion component discrepancy 0.0409492 / 0.0867082. Do not present these as an end-to-end exact reconstruction. The read order demonstrably mixes differing cached poses; remaining compose discrepancy is not fully explained.

Checks: Python compilation; original solver replay rerun unchanged; graph adapter enforces unique source identity, alias membership, 120 rows, exact same-graph connections and aggregate discrepancy below 0.0002 for this capture.

Remaining: full optional-input factory semantics (slots remain numeric), source clip-channel inputs for this PC family, downstream dress anchor composition/dynamics, scale helper integration, Unity skeleton basis conversion and clip export. No production Unity assets modified. This is a bounded graph adapter, not a full original animation decoder. Next work can proceed offline; no new capture requested.
