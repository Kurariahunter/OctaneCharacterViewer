# Elsa named-control mapping — 2026-10-14

## Established structural results
The older source model has DataNodeLinks (490 bytes), with 90 non-0xFF entries. Those entries are a complete permutation of the 90 ConnectionMapUsedDataNodes slots. Under the candidate interpretation DataNodeLinks[port] -> used slot -> DataNode, all 243 commands across six parsed idle samples resolve to existing source model controls. The discontinuous idle remains flagged despite its successful mapping.

Examples: head port 308 -> DataNode 246 -> Cntrl_Head_Grp; neck port 370 -> DataNode 240 -> Cntrl_Neck_Grp; spine port 397 -> DataNode 219 -> Proxy_Cntrl_Spine1. These are procedural controls, not yet final skin-bone transforms. The mapping has not been traced through the complete original runtime loader.

## Record flag evidence
All 87 records carrying the 0x10 flag in these six idle samples target Float DataNodes and contain descriptor 0x001A. Other mapped idle targets are Transform/Dilation controls. The original command jump table maps low nibble 0xA to 0x532693; that path resolves a compatible value node and writes one float at object +0x34. This supports a scalar-control classification, but the on-disk flag's loading/lifetime semantics remain unresolved. It is preserved, not discarded or claimed as fully understood.

The older model has no separate reverse lookup table of the kind used by the newer Yoda file. The permutation consistency check is structural evidence, not an independent bidirectional runtime validation.

## Native head/neck sampling
Active and passive idle each have 61 evenly spaced times. Their head and neck controls produce 244 rows in elsa-head-neck-native-samples.csv. Dynamic curve values come from isolated original routine 0x522CF0; static operands are read from the bounds-checked source float pool. Convention-2 rotations come from isolated original routine 0x40E180. All inputs/results are finite and quaternions pass unit-length tolerance. This avoids the approximate Python interpolation for these samples.

These are source controller rotations. They have not passed through the rest of Elsa's procedural graph, base/additive composition, skin-bone evaluation or Unity coordinate conversion. No playable Elsa animation or production importer change has been made.

## Next step
Trace the mapped head/neck controls through their transform connections to the skin bones and validate one pose against the model's stored/bind references. Only then create a head-only Unity review clip. Keep the 0x10 flag and unsupported layouts as explicit unresolved cases.
