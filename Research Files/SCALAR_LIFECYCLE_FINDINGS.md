# Scalar contributor lifecycle and naming correction — 2026-10-21

## Verified preservation

`test_scalar_contributor_lifecycle.py` executes native removal5337A0 and insertion5440C0 on a preallocated synthetic contributor table. Six initial states cover fade0/0.25/1 with bit31 both clear/set. Removal, re-addition and absent-controller removal preserve the processor's flags, saved fade and scalar output exactly in all18 operations. Counts and return values are checked. This does not cover allocator paths, default-network rebinding or all actor activation code.

Constructor5336F0 initializes flags+18 to0000FFFF, saved fade+34 to0, and output pointer+30 to null. It does not establish bit31 as an automatic first-evaluation flag. Contributor insertion/removal alone must not be used as a reason to clear the viewer's scalar state.

## Correction to earlier terminology

Previous notes/API used `first_evaluation` for bit31 at processor+18. That lifecycle meaning was not established. The verified meaning is **fade bypass**: the native blender skips525450 and selects full replacement when it is set. A native test with partial factor0.5 confirms the bit remains set after evaluation; the operation is not a demonstrated automatic first-frame reset.

The Python argument is now `bypass_fade`, and state-bank field is `bypass`. Captured processor flags still drive the same native instructions, so earlier numerical parity results remain valid. Update: SCALAR_BINDING_ASSIGNMENT_FINDINGS.md verifies constructor initialization with bypass clear; the viewer state wrapper now uses that clear default. Initial output0 remains an explicit fixture. Existing controller states are not reset on clip selection. Native state storage is retained between ticks. Earlier relevant notes were corrected to use the behavioral name.

## Validation

- Six native contributor lifecycle cases /18 operations pass.
- Original temporal native tests cover increasing/decreasing/zero/full fade and preserved bypass.
- State wrapper continues to reproduce306 recorded final values exactly.
- The saved full-weight viewer bake does not change due to this naming correction.

Machine report: `ElsaSceneResearch/ControllerState/scalar-contributor-lifecycle-validation.json`. The scoped pattern searches for reset writers did not identify a proven bit31 setter on this type; raw byte matches in other classes are not evidence. This is an unresolved boundary, not proof that no setter exists.

Next: trace the default-network/channel-binding setup that writes processor+18/+1C, or take a narrowly targeted write observation once the relevant live blender is reidentified. The existing bridge can read state but cannot hook writes. No generic movement capture is needed.
