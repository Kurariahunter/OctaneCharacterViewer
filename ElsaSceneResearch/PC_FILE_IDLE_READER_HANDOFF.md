# File-only PC idle reader checkpoint

## Completed

The installed-PC Elsa active and passive idle ClipDataBlocks now parse and sample directly from extracted game OCTs plus the matching model OCT. No live captures or game process reads are used. Hash-pinned original executable routines run offline in Unicorn for scalar curve evaluation and convention-2 Euler-to-quaternion conversion.

Run `Read PC Idle Files.cmd` in this folder to regenerate `pc-file-idle-channels.json`. It reads the independently extracted matching PC files in InstalledGameAssetCheck. It does not import or modify Unity assets. Python and the existing research dependencies must remain installed at their current paths.

Tools: pc_clip_decoder.py, native_pc_clip_math.py, read_pc_idle_files.py, test_pc_file_reader.py.

## New format findings

The PC ClipDataBlock command lists are packed, unlike the older downloaded asset family's interleaved command records:
- Dynamic header stores byte extent relative to the start of the register/command block, and command count.
- Packed uint16 command codes precede the descriptor stream. Upper 3 bits give descriptor count; low 13 bits identify the port. No extra record flags are inferred.
- Static table similarly stores a count, all packed command codes, then all opcode/index descriptors.
- Curve blocks retain the previously investigated knot/quantized-control-point structure.
- Engine routine 0x5232e1 quantizes time to uint16 ticks, with float32 subtraction/division/multiplication order and truncation, before segment lookup. A continuous-time approximation differed by up to 0.0220372 on steep PC scalar curves; reproducing time quantization reduces the numerical comparison error to below 0.000001.

PC model port binding differs from the old 8-bit DataNodeLinks layout:
- LocalUsedDataNodeIndices, LocalToPortIndices and PortToLocalIndices are little-endian uint16 arrays.
- LocalUsedDataNodeIndices indexes ConnectionMapUsedDataNodes.
- Forward and reverse mappings are checked for all 112 mapped model ports; local-used indices form a bijection.
- HeaderLayout and HeaderStringIndices yield complete source paths. These remain structural bindings, not a claim that the complete original loader or blend system has been executed.

## Results

Active: 4.199999809 seconds; 28 curve blocks; 50 registers; 24 timed records; 99 constant records; 127 samples at nominal 30 Hz including endpoints.
Passive: 6.166666508 seconds; 18 curve blocks; 45 registers; 24 timed records; 64 constant records; 186 samples including endpoints.

All 48 timed records map to source controls. Constant-channel ports absent from this model's Main link map are retained explicitly with null target/path, not guessed or discarded:
- Active: 27, 28, 122, 279, 667, 668, 851, 852, 853, 854.
- Passive: 279, 280.

Three-time sampling detects movement on 20 active and 24 passive control ports. Output stores raw per-component channels keyed by opcode, not merged final bone transforms. Full-vector constants and component overrides are both preserved; downstream evaluation must apply the correct precedence/default behavior.

Validation: 276 independent Python-vs-native scalar curve samples; maximum absolute error 0.0000009230573. Twelve truncated-payload/invalid-time cases rejected. Python compilation and full file-only generation passed. Detailed checks in pc-file-reader-validation.json.

## Remaining milestone

This is a working bounded clip-channel reader, not a complete animation player. Next: apply these PC controls to the PC procedural graph, initially head/neck or torso outputs, and emit a small file-only bone-motion preview. Constant ports outside the Main map, base layers/defaults, remaining graph operators, procedural dynamics, exact skeleton basis and Unity clip generation are not resolved by this checkpoint. No claim of final full-body parity with the game.

Source payloads:
- Active SHA256 f31d6d2dd86be1963751df3c01ad623d80b713e3f3efef624c4ccead47c16e3d.
- Passive SHA256 6f4dbdadc6d5102655d64a5538f8a661a7e4fa08cd43e8224c79f9f8f52a6d98.
- Model SHA256 38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d.
