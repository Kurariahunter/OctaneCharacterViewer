# Rotor offset order resolved for the tested native policy

## Result
The original UnitRotor3d OffsetPolicy selects the diagnostic OffsetRight candidate. Under the project's transposed quaternion-matrix convention, M_out = M_input @ M_offset. In standard Hamilton xyzw quaternion notation this is q_out = q_offset * q_input. Matrix-order labels and Hamilton multiplication labels are therefore reversed; do not transpose the conclusion when implementing in Unity.

## Evidence chain
ProcessorNode::UnitRotor3dOffsetProcessor is registered at 0x501F7A with factory 0x4F2FF0. Runtime RTTI identifies CommonBasisArrayProcessor<UnitRotor3d, OffsetPolicy<UnitRotor3d,UnitRotor3d>>. Its vtable is at 0x1B2D3AC; execution slot 16 points to thunk 0x4C18B0, which calls 0x4BD400. The latter contains the actual quaternion multiply. Authored Elsa processors list Input, Offset, Output, in that order. Direct emulation supplies those two operand slots and the output slot accordingly; it does not run the entire asset loader.

The isolated original processor passed 103 quaternion-pair tests. 101 cases distinguish the two orders. Maximum quaternion component error was 8.13e-8; maximum source matrix error was 2.58e-7. Inputs included mixed-axis and deterministic randomized unit quaternions. Identity/commuting cases alone would not have established this result.

See rotor-offset-native-validation.json for actual inputs and native outputs, validate_rotor_offset_native.py for the reproducible test, and rotor-offset-disassembly.txt for the reference instructions. The executable SHA256 is pinned in the test.

## Unity result
Use the ACTIVE / offset RIGHT and PASSIVE / offset RIGHT instances in the existing comparison. LEFT is retained as a nonmatching comparison; it should not be selected for the supported offset policy.

Two ready-made native-order diagnostic prefabs are installed in Assets/ElsaHeadResearch/ElsaNativeOrderPreview. These are byte-identical copies of the previously validated RIGHT prefab contents with new asset identities, sharing the same tested clips, controllers, skin mesh and materials. Existing scene instances and the four-way comparison were not changed.

## Remaining limitations
This resolves the tested UnitRotor3d OffsetPolicy, not every rotation/relationship processor. The preview still applies explicit bind-relative baseline alignment; the original graph pose differs from the skin bind pose. Helper parenting, full-body graph evaluation, scalar-record loading, animation layering and source-faithful rest-pose transfer remain unresolved. This is not a complete original-game animation importer.
