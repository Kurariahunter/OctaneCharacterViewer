# Elsa layer and scheduling audit

2026-10-16. Follow-up to DRESS_REFERENCE_AUDIT_HANDOFF.md.

## Result

No confirmed corrective change. Mesh, weights, preview clips and production importer unchanged. The active bulge remains unresolved.

Source fro_elsa.bent (41522 bytes,1890 records) decodes to exactly the file boundary. Inventoried27 channel declarations,27 model bases and441 file entries. STANCE, STANCE_ACTIVE2PASSIVE and STANCE_PASSIVE are in Core:BaseMobility and directly reference the corresponding Elsa motion OCTs. None of these three entries declares Layers or Filter. This is declaration evidence only: it does not show what channels the running game enables or prove the absence of another game-driven layer.

FullBody declares PriorityOrder5, ChannelIndex0. FullBodyBlends declares PriorityOrder4, Weight0, ChannelIndex4. FeetInterface declares PriorityOrder2, ChannelIndex9. Several channels are named Additive, but their names alone do not establish their runtime math. Model bases share Anchor/Anchor-Main and route to their named channels. Do not interpret channel priority direction, additive composition or runtime active weights without tracing consumers.

## Static scheduling boundary

611 source processors,845 producer/input edges. Explicit graph is acyclic. Adding the two previously resolved hidden sibling Orientation dependencies produces two feedback components:

- Left: DynamicChain585, Difference428, InverseVector427, Aim426.
- Right: DynamicChain587, Difference437, InverseVector436, Aim435.

These are genuine scheduling boundaries not represented by serialized DataNodeRefs alone. Previous-frame quaternion feedback remains qualified until original engine ordering is traced. Hair's cached reference is intentionally excluded here because this audit does not independently resolve it.

UpperDress650 and655 each have53 processor ancestors in the explicit dependency graph. Neither ancestry includes a DynamicChain or intersects the augmented feedback components. Therefore the observed skirt feedback cycles have no demonstrated upstream route to alter UpperDress poses. This does not rule out external runtime writes or omitted dynamic dependencies.

## Another input-loading boundary

ConnectionMapUsedDataNodes has90 slots. DefaultDataIndices has180 bytes (90little-endian words), DefaultData68 bytes (17 floats). Word patterns: see connection-default-table-inventory.json. Pool consists of identity-like quaternion/translation/scale values and scalar zero. This is not evidence of an obvious non-neutral correction. A packed component-mask/offset interpretation is plausible but unvalidated. Existing evaluator uses stored DataNode fields as untouched fallback; its equivalence to channel defaults and blending has not been demonstrated through the executable loader. Do not apply table values based on this inventory alone.

## Reproduce and next step

Run audit_elsa_layers_schedule.py -> elsa-layer-schedule-audit.json. It decodes the original archive BENT, checks exact byte consumption, captures declarations with record offsets, constructs graph dependencies, identifies cycles and asserts no cycle reaches the upper-dress ancestry. Run inventory_connection_defaults.py -> connection-default-table-inventory.json. Existing read-only originals and Python research dependencies required.

Next concrete executable target: connection-map default/channel loading and the blend consumer that applies FullBody/FeetInterface inputs before procedural evaluation. That will test the remaining untouched-default assumption and establish runtime channel semantics. The BENT inventory is reusable for selecting additional motion families; it is not a BENT player or final animation decoder.
