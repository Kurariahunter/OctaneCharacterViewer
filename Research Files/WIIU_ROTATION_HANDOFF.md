# ReverseEulerZXY reconstruction — 2026-10-24

This pass confirms the scalar expression used by the Wii U order2 rotation path. No production viewer animation changes.

## Source evidence

- BaseClipProcessor::ConvertEulerToRotor0x023265B4 chooses Types::ReverseEulerZXY::AsRotor0x02013520 when order code=2.
- AsRotor calls Euler3d::SinCosHalfAngles0x020122F8. The routine uses multiplier0.5 at0x10000240, then calls sinf/cosf for each input component. Inputs are radians.
- Sines are written to the first output vector and cosines to the second. AsRotor’s scalar products, fused multiply-add/subtract and negations identify quaternion components, stored in stack order x,y,z,w before the final paired-single copy.
- Generic Capstone does not fully decode the paired-single load/copy instructions. The scalar formula and final component stack order are directly visible; no bit-exact PowerPC emulation is asserted.

With sx=sin(x/2),cx=cos(x/2),etc:

```
qx = -(sx*cy*cz + cx*sy*sz)
qy = -(cx*sy*cz - sx*cy*sz)
qz = -(cx*cy*sz - sx*sy*cz)
qw =   cx*cy*cz + sx*sy*sz
```

A positive single-axis angle therefore produces a negative corresponding quaternion vector component. Do not substitute a generic positive Euler rotation or Unity Euler call on the basis of the ZXY name alone.

## Cross-platform numerical check

validate_rotation_pc_native.py compares wiiu_rotation_math.py to the original PC native order2 routine0x0040E180 through the existing SHA-pinned offline harness. Cases: identity, three mixed-axis witnesses, twelve signed single-axis tests,128deterministic random mixed-axis tests. Total144.

All pass; maximum component discrepancy9.833505443257451e-08. Double-precision reconstructed quaternions are unit length within1e-12. A deliberately incorrect positive XYZ convention fails a mixed-axis witness by approximately0.97097 even when global q/−q equivalence is allowed. No fitted offsets or normalizations were used to hide a mismatch.

This validates the reconstructed mathematical convention against PC executable behavior. It does not prove bit-identical Wii U sinf/cosf, FMA rounding, matrix conventions or downstream graph composition.

## Usable output

elsa-control-quaternions.json adds84derived typed control quaternions across the three previously exported source-control snapshots. Original Euler operands/order codes are retained. Static constants and evaluated scalar channels remain present.

These are character controls, not final skin-bone poses. Interior cubic sampling still uses the documented Python approximation rather than original native time quantization. Downstream relationships, IK, local/world transforms and palette mapping have not been run for these Wii U snapshots. Existing PC viewer playback remains unchanged.

## Next target

Use the source control paths to follow Transform/Float outputs through actual Wii U relationship processors and skin-bone world matrices. Reuse the separately validated eye decoder for its supported relationship layout, and compare processor identities/connections against the existing PC evaluator before attempting a whole-character playback adapter. Keep known working PC previews and source-only experiments separate.

Artifacts: wiiu_rotation_math.py,validate_rotation_pc_native.py,rotation-native-crosscheck.json,elsa-control-quaternions.json and complete-byte disassembly/fingerprints for49routines.
