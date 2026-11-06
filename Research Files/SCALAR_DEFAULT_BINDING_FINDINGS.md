# Observed scalar default binding — 2026-10-21

## Live field audit

All306 scalar entries in capture201439 have processor+18 bit31 clear. The low channel indices are33..38 for left-hand ports483/485/486/487/488/489 and39..44 for right-hand ports510/512/513/514/515/516. All point through processor+1C to default-network data1D92974C in this session.

The read-only bridge rechecked PID104600/module MZ, the right-hand scalar processor's rebased Float-blender vtable, index39 and default pointer before following that pointer. The twelve default lookup entries at default+0C, indexed33..44, all contain16. Masking with1FFF yields scalar index16. The scalar table at default+14 holds0.0 there.

Evidence: `ElsaSceneResearch/ControllerState/live-scalar-default-binding.json`, including original read responses and decoded slot values. This is a current read snapshot; it is not a synchronized activation trace or evidence that all characters share these defaults. Addresses expire when the process/session changes.

## Native replay

The original Float blender's residual-default path at4E33C4..4E3403 reads precisely this indexed structure when the accumulated unflagged source weighting leaves a residual. `native_pc_blend_replay.py` now supports an explicit optional scalar default fixture with that layout. It remains absent by default for existing tests.

`test_scalar_default_binding.py` passes15 original-instruction cases across defaults0/2/-4 and weights0/.25/.5/.75/1. For unit temporal fade, the tested output is the weighted source plus residual default. For example, source10, weight.25 and default2 gives4. This is separate from the subsequent stateful temporal-fade operation.

This does not add a pose correction. Full-weight idle previews have no residual default contribution and remain unchanged. No inferred fist or neutral-pose value was substituted for the live zero values.

## Unresolved writer

Scoped static searches and channel-binding inspection have not identified a proven writer for the fade-bypass bit. Raw instruction-byte matches in unrelated types were rejected after instruction-boundary/type checks. No claim is made that such a writer does not exist.

The useful narrowed boundary is now the assignment of the composite processor+18 field and default-network pointer+1C, with a concrete live object/index layout. Finding a writer requires a type-confirmed binding caller or a targeted write observation; the read-only bridge itself cannot install a write hook. Do not reset blender state on clip changes based on these observations.

Reports: `scalar-default-binding-native-validation.json` in ControllerState and the earlier `scalar-contributor-lifecycle-validation.json`. No new capture is required to verify the default lookup and numeric residual operation reported here.
