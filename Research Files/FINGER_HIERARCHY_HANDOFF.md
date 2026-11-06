# Finger hierarchy native comparison

Preview diagnostic snapshots now include a hierarchy_audit. It traces dependencies from Thumb/Index/Middle skin outputs, stops at the known hand-world outputs and relationship outputs when encountered, and compares supported two-input chain Dilation operators with original native routines. Other operators are listed as unverified by this particular audit. The dependency traversal can reach shared body/control ancestors; these are not all finger-local nodes.

The first attempt reported a mismatch at node248, Cntrl_Spine1-to-Body. That was a **fixture setup error**, not evidence of a production pose bug: ConcatenateChainInverseDilation requires its normal-input count at processor+0x1C. Earlier research already documented this field, but the new generic audit had omitted it. The audit now derives the count from Input[] versus InvertInput[] source attributes. The shared native helper gained an optional normal_input_count argument; existing callers retain their previous behavior when it is omitted.

With the corrected fixture, the native-default run bake passes all existing invariants. Twelve supported operators per snapshot (start/mid/end) give 36 native comparisons, maximum matrix error 2.2801798416072216e-7. Full clips payload exactly matches all 19 pre-diagnostic samples. No hand rotation, scalar value, parent relationship, skinning or source composition was altered.

This narrows the investigation: the tested matrix multiplication/inversion operations agree with native math for supplied inputs. It does not verify every downstream operation, the active game's finger scalar values, or upstream layer weights. Quaternion unit length and these hierarchy comparisons cannot establish visual game parity.

Artifacts: NativePreviews/native-default-run-finger-audit.json (now includes hierarchy audit), finger-hierarchy-validation.json, ElsaSceneResearch/pc_finger_transform_audit.py, and optional argument in native_pc_dress_math.call.

Next compare the active game's finger scalar ports and layer contributions with the recorded composed inputs, or extend independent comparisons to listed unchecked operators if static evidence points there. Do not introduce manual offsets or change replacement/addition merely from filenames. Diagnostic reports are included in future bakes; the current native baseline remains unchanged.
