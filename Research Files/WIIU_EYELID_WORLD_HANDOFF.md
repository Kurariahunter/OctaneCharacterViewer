# Evaluated eyelid converter checkpoint — 2026-10-24

The generated converters are now evaluated instead of substituting their stored identity values. Original PC forward Compute is `0x004D7310`, identified through the TransformDilationWithDilation registration and typed vtable. Wii U Compute `0x021D3EB0` calls BasisConvert `0x021C9B68`, which swaps the arguments into Dilation addition `0x0214B818`. Complete byte-covered disassemblies are archived; generic PPC decoding still has paired-single limitations.

48 deterministic native PC fixtures include noncommuting rotations, translations, positive nonunit uniform scales and identity controls. Independent column matrices match converter @ input. Maximum absolute component error: 8.095007090203055e-07. This establishes the bounded operation; it is not conjugation. Results: dilation-converter-native-crosscheck.json.

The source graph replay now evaluates the actual converters 272, 276, 280 and 284, the four head-local eyelid outputs, and their world Dilation outputs using Head 388. Three clip times produce 12 finite world matrices. Results: wiiu-head-eyelid-world-fixture.json. Source matrix associations and skin influence identifiers are retained as provenance, not transplanted into the PC palette.

The old local-output fixture used stored identity converters and remains historical evidence only. The old head-only report remains a previous checkpoint. This new replay still uses explicit source-default leaves, approximate interior clip times and original PC numerical routines on endian-converted Wii U data. It does not establish live Wii U actor state, scheduling, complete palette or rendered parity. No production viewer behavior or game files changed.

Next: validate these matrices against the authored output conversion and skin binding, then expose a clearly labeled bounded preview. Do not apply finger offsets or claim a complete native engine.

Reproduce from project root:
```
python WiiUResearch/AnimationViewerResearch/validate_dilation_converter_pc_native.py
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_head_fixture.py
```
