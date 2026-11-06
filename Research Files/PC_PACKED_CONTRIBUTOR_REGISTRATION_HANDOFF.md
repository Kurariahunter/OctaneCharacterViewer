# Packed contributor registration checkpoint — 2026-10-18

Continues PC_INDEXED_FILTER_APPLICATION_HANDOFF.md. Same hash-pinned installed PC executable. Preferred VAs use base 0x400000. Manifest includes RVAs and byte hashes.

## Native entry builder found and executed

Function 0x5440c0 writes the 8-byte contributor entries consumed by 0x4e35d0. RTTI on the containing object identifies Samurai::BlenderBase.

Inputs: this = target BlenderBase, argument 1 = controller, argument 2 = source index, argument 3 = filter index. Packed second word is (source & 0xFFF) | ((filter & 0xFFF)<<12). New entries have upper byte zero; later blend processing may set high bits. Large/negative index arguments are masked, not validated.

The builder sorts entries by ascending controller priority at +0x34. At equal priority, flag +0x39 = 0 precedes nonzero flag entries in the tested boolean domain. Equivalent entries retain insertion order in our finite fixtures. A null controller is ignored, and once count reaches 50 no further entries are added.

The table lives at BlenderBase +0x24, count +0x28 and capacity +0x2C. Tests preallocate capacity 64 so allocator paths are not needed. Original native vector insertion/move helpers execute without replacement. This does not test heap growth, nonfinite priorities or all flag byte values.

Evidence: validate_pc_contributor_entry_builder.py; 49 packing combinations, 6 sorted insertions, null entry and 50-entry cap checks.

## Source-to-filter mapping step verified

Registration function 0x4cea30 iterates source slots. The target blend output is fetched from the destination container and type-checked. The mapping object is reached through controller +0x20.

In original instruction window 0x4ceabe..0x4ceadc:

- source slot is used directly as argument 2;
- mapping pointer is read at map object +0x38;
- mapping count is read at +0x3C;
- mapped entries are uint16;
- mapped[sourceSlot] supplies argument 3;
- out-of-range slots and entry 0xFFFF take a -1 path, which the builder packs as filter index 0xFFF.

Ten original-window cases exercise reordered source/filter values, values requiring masking, sentinel 0xFFFF and out-of-range source slots. The window invokes the real builder. This proves the runtime map read and entry transfer, not the serialized meaning/ownership of the mapping object.

Do not silently convert invalid/sentinel map entries to coefficient zero or index zero. The observed builder path retains packed 0xFFF. The consuming routine does not check filter-array bounds in the inspected read, so a future independent loader must validate mapping/filter extents before evaluation. This is not evidence that valid game assets contain an invalid map.

Function 0x4ceb00 follows a selective per-source enable array and the same mapping/build call; function 0x4bcc00 uses this map when invalidating/reordering existing entries through 0x544190. These additional paths are statically traced; only the stated window was executed in the new tests.

## Builder -> blend integration verified

The offline replay adapter accepts build_entries=True to invoke original 0x5440c0 for each contributor before original 0x4e35d0 consumes the table. The previous manually prepared table path remains the default for historical fixture compatibility.

18 indexed source/filter/factor cases match their prior outputs when entries come from the native builder. A further 18 reversed-input cases also match because the original builder restores the appropriate priority/flag ordering. No final motion is corrected by manually swapping sources or changing quaternions.

Scope remains controlled: one unflagged base + one flagged delta, equal priority, unit scale, fixed +0x30 scalar, no default-network or actor scheduling/temporal fade. This is producer-consumer interoperability for known numeric fixtures, not whole-engine/game parity.

## Remaining connection to source files

The remaining index question is now specifically how the map object at controller +0x20 gets its uint16 source-slot-to-filter-index table (+0x38/+0x3C) from the authored connection maps and port tables. We must verify that before labeling a filter array entry as a particular bone, node or port. Source slot, filter index, bone palette index and port ID remain distinct namespaces.

Next: identify/map the construction of that object, compare serialized table order with a known source network, and validate the full source-to-packed-entry chain. Live parameter writes and external clip-control precedence remain open as documented in earlier checkpoints. No broad live capture requested yet.

## Viewer and reproducibility

Viewer motion is unchanged. The new optional native-builder path is in the research replay harness, not silently enabled for source previews without authored mappings.

Run validate_pc_contributor_entry_builder.py and validate_pc_indexed_filter_blend.py. Reports: pc-contributor-entry-builder-validation.json and pc-indexed-filter-blend-validation.json. pc-packed-contributor-registration-manifest.json records six code regions and owner RTTI.
