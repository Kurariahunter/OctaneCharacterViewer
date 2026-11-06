# Geometry-copy skin-slot remap — 2026-10-22

The load-bound62-slot object is RTTI `Renderer::GeometryNode`, preferred vtable0x1B29924. Vtable slot+0x0C resolves to0x478580. This allocates a new geometry via0x4743F0 and calls0x475D40 with the source in ECX and destination as an argument. This establishes a concrete copy path; no claim is made that it is the sole active actor path.

In0x475D40, source/destination descriptors begin at object+0x120; skin-table relative offset is the word at object+0x12E. The nested table starts with count and pointer-array relative offset. The loop0x475EF0..0x475FF3 resolves each source node's identity through0x4B46D0, consults a registry rooted at0x21AF260 with count0x21B725C, checks identity/generation fields and node type, then assigns the destination slot through0x5730E0. Inverse-bind data is subsequently copied as count*64 bytes at0x47600E. This is independent evidence for why the load table can remain unchanged while a runtime copy uses other nodes.

Original instruction subrange0x475F14..0x475FA5 passes8 isolated cases: tagged/untagged replacement; registry miss/out-of-range; two identity mismatches; empty replacement; wrong type. Registry misses/identity mismatches retain the old node; accepted replacement pointers have the low tag removed; empty/wrong-type replacements become null. The fixture begins after source identity lookup and does not validate registry population, whole-copy semantics or final rendering.

Evidence: ControllerState/geometry-skin-remap-disassembly.txt and native-skin-slot-remap-validation.json. Test: test_native_skin_slot_remap.py. A fresh bridge read returned registry count0 outside the copy, supporting the need to observe this transient path rather than scan idle registry contents. It does not by itself prove when/how the registry is populated or cleared.

## Prepared live probe

`F:/DisneyInfinityPortalTest/OctaneLiveInspector/CheatEngine/DI3_SkinRemapLogger.lua`

One read-only hardware execution breakpoint at preferred0x475FD8, after destination assignment. Source object is stack+0x10, destination stack+0x2C, EDI/EBX are corresponding nested tables, ESI is influence index. The logger verifies both object-to-table equations and both counts62 before recording source/destination pointers, node headers/stamps, registry count and slots. File-order bone names are not assigned by the logger.

F8 starts; reload Elsa's scene; F9 stops. Automatic90-second/124-event limit. Capture filename starts `ce_skinremap_`. The successful completion beep follows saving and breakpoint removal. Known recent logger hotkeys are retired. Unrelated existing breakpoints cause rejection. No memory/code writes, forced poses or live function invocation.

Four Lua CE mock cases pass: valid context with dedup; bad owner rejection; signature rejection; installation failure. Cleanup and beep ordering are checked. Reports: CheatEngine/skin-remap-mock-validation.json. The probe is prepared and tested with mocks, not yet validated against a live remap hit.

Next capture this different copy/remap boundary, hash-link its source nodes to the previous load-bound object and follow its destination nodes toward the moving hand network. Do not repeat the load-only skin logger as if it observes runtime copies; do not claim GPU palette proof from a geometry copy alone.
