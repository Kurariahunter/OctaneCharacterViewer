# Wii U animation output / source-port mapping — 2026-10-24

Continuation of RESULTS.md. No production animation evaluator or viewer playback changes in this pass. All source files remain unchanged.

## Confirmed native dispatch structure

ReferencedTrack::DispatchToResults at0x02383D24 reads each packed output word as low13bits port and high3bits descriptor count. It bounds-checks the port against the MaskedIndexArray extent, rejects0xFFFF entries, applies the stored mask and uses the resolved index to select a52-byte BlendArray result. The result presence mask is at+0x30. Unknown/unmapped channels are skipped by advancing over their descriptors; they are not assigned to an arbitrary bone.

The descriptor class controls width: class0 uses4bytes; classes0x1000/0x2000/0x3000 use8bytes. This sample uses only class0 and0x1000. The other classes are not decoded into guessed transforms by our inspector.

For scalar component descriptors, source mode0x10 reads evaluated registers; the constant case reads the float pool. Euler class0x1000 chooses each axis operand independently from those two arrays, extracts rotation order from opcode bits6..8 and calls BaseClipProcessor::ConvertEulerToRotor at0x023265B4. We retain raw Euler operands/order instead of asserting a new rotor-conversion implementation.

Static position-vector writes mark bits0xE; quaternion writes mark0x100; scale-vector writes mark0x70. These are presence bits, not permission to overwrite unrelated components. Some quaternion/paired-single instructions are not decoded correctly by the available generic PowerPC disassembler, so no full floating-point operation equivalence is claimed.

## File-backed binding

Extracted fro_elsa.oct from the same Wii U character archive as elsa_bm_idle_specific01.oct. Main BaseDataNodeLinks uses characters/biped/biped.ct. Parsed LocalUsedDataNodeIndices and LocalToPortIndices as big-endian16-bit arrays; audited both against PortToLocalIndices and ConnectionMapUsedDataNodes. The110mapped source ports form a bijection over the110declared used nodes. Reverse table extent935, with825unmapped0xFFFFsentinels.

The clip has53timed and58static command records. All53timed records and56static records map to existing source controls. Static ports279/280 have explicit0xFFFFsentinels and stay unmapped, consistent with native dispatch. The record counts include repeated ports across static/timed stages; they are not111unique bones.

Example timed bindings:

| Port | Source data node | Authored control path |
|---:|---:|---|
|90|234|Anchor / Cntrl_Body / Transform|
|497|294|Anchor / Cntrl_Hand_Left / Transform|
|524|314|Anchor / Cntrl_Hand_Right / Transform|
|284|340|Anchor / Cntrl_Eye / LowerLidLeft|
|285|337|Anchor / Cntrl_Eye / LowerLidRight|
|290|338|Anchor / Cntrl_Eye / UpperLidLeft|
|291|339|Anchor / Cntrl_Eye / UpperLidRight|
|483|289|Anchor / Cntrl_Hand_Left / Index1|
|510|309|Anchor / Cntrl_Hand_Right / Index1|

This confirms paths structurally; it is not another live finger comparison or a finger correction. Those paths are scalar/transform controls whose downstream relationships still produce skin-bone transforms.

## Outputs and checks

- map_wiiu_clip_ports.py reproduces source-port map, static constants and timed operand references.
- elsa-output-port-map.json contains all111command records with source paths; all operand indices and command extents validated.
- elsa-raw-control-samples.json contains3raw control samples at clip start/mid/end. Scalar curves and static values are resolved; Euler operands retain order code and are NOT converted into final bone rotations.
- Some curve domains differ from the overall clip range. Operands outside their individual validated domains are null with no guessed wrap/clamp behavior. Cubic evaluation is Python arithmetic, not a proof of native time quantization or PowerPC execution.
- Disassembly coverage expanded to46functions.18instruction records remain undecoded data, and PowerPC paired-single instructions may be mislabeled as later-ISA operations by Capstone. Coverage JSON records byte extent so a decoder stop cannot silently omit a function tail. Original code bytes remain available through the RPX sections. Treat integer masks, table offsets and named calls as the direct evidence; floating-point engine parity still needs an appropriate native reference.

Next bounded target: use the labeled Wii U curve range/boundary branches to explain those out-of-domain operands, then compare against existing PC native curve fixtures. After that, connect typed control outputs through relationship/IK/world-transform processors into a full palette. No new Cheat Engine capture is required for the current file/label work.
