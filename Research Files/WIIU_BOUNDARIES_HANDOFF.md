# Wii U timeline boundaries and Euler dispatch — 2026-10-24

Continuation of OUTPUT_MAPPING.md. Research-only: no changes to PC viewer playback or source game assets.

## Confirmed flags0 boundary behavior

BaseClipProcessor::ComputeTimelineCICD at0x0231E7BC:
- Before start:0x0231E8A4 tests time<rangeStart; low3flag bits choose behavior. Mode0 branches to0x0231E908. It reconstructs the first quantized control value as bias+firstSignedShort*scale, writes each component and resets segment cursor0.
- After end:0x0231EDBC tests time>rangeEnd; mode bits3..5 choose behavior. Mode0 branches to0x0231EE58. It writes metadata component field+4 (stored end value), and sets cursor to segmentCount−1. It does not evaluate the last cubic at t=1 for an out-of-domain sample.
- At the exact start/end, execution stays on the ordinary interior path. Strict comparison matters; no epsilon was added.
- Other branches include linear extension, fmod-based cycling and a reflected cycle, but their complete semantics are NOT admitted by the inspector in this pass. It still rejects nonzero curve flags.

The short curve domains are real: many source curves end between4.8 and5.0333333seconds while clip duration is5.0666666seconds. Their final held values therefore contribute to a valid whole-clip sample.

## Original PC native-code cross-check

validate_boundaries_pc_native.py transcodes each Wii U curve’s header/scalars/knots/coefficients to the corresponding little-endian PC layout, preserving all numerical values. It calls our existing SHA-pinned original PC0x00522CF0 scalar routine through the established offline Unicorn harness. It does NOT run the Wii U instructions.

All72curves x before/after =144checks passed. Maximum start-hold discrepancy0; maximum stored-end discrepancy0. This corroborates the independently traced Wii U branch semantics. Native PC EXE hash and individual outputs are in boundary-native-crosscheck.json.

The Wii U inspector now applies only these confirmed flags0 start/end holds. map_wiiu_clip_ports.py regenerated three whole-clip raw control samples:1212scalar/Euler/constant operands, all finite/resolved, no nulls. The two explicitly unmapped static ports remain excluded rather than assigned to a guessed control.

Interior Python cubic arithmetic still does not claim exact native uint16time quantization, fused arithmetic or PowerPC output equality. Command outputs are control channels, not final skin-bone matrices.

## Named Euler order dispatch

Completed static branch tracing of BaseClipProcessor::ConvertEulerToRotor0x023265B4. It selects these named AsRotor routines:

| Order code | Named source type | Wii U callee |
|---:|---|---|
|0|ReverseEulerXYZ|0x02013930|
|1|ReverseEulerYZX|0x02013B60|
|2|ReverseEulerZXY|0x02013520|
|3|ReverseEulerXZY|0x02013A48|
|4|ReverseEulerYXZ|0x020131FC|
|5|ReverseEulerZYX|0x02013638|

The measured Elsa idle’s dynamic Euler descriptors use code2, so the executable labels identify their type as ReverseEulerZXY. This is stronger evidence than guessing Unity Euler order. It is NOT enough by itself to choose quaternion storage signs, transpose matrices or change viewer rotations: Types::ReverseEuler conventions and AsRotor arithmetic still need direct comparison. Unsupported paired-single instructions are retained as raw data records in the disassembly, and some are mislabeled as newer ISA mnemonics by generic Capstone.

## Next bounded task

Inspect Types::ReverseEulerZXY::AsRotor and verify its quaternion layout/sign against the existing PC order2 routine using noncommuting test angles. Then connect typed control channels to the already identified downstream relationship/IK/world processors. Keep this independent of parked finger visual research and do not add arbitrary pose offsets.
