# Native parameter binding and filter-object checkpoint

2026-10-18. Continuation of PC_EXE_NORMALIZED_PARAMETER_HANDOFF.md. EXE SHA-256 f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705. Addresses are preferred VAs, base 0x400000; manifest includes RVAs.

## Confirmed runtime identities

MSVC RTTI identifies Samurai::FloatParameter (vtable 0x1b38e4c), Samurai::KeyBlendTrack (0x1b38e94), Samurai::ReferencedTrack (0x1b38ec4), and Samurai::Filter (0x1b2f388). Filter has one confirmed virtual slot in this table, a destructor; adjacent text must not be misread as additional slots.

## Parameter lookup and rebinding — native-validated

0x5439e0 searches the parameter container's pointer array at +0x94, count +0x98. It skips null slots and returns the first exact case-sensitive name match. The parameter name getter 0x59fb50 reads a name block pointer at parameter +0x0C and returns characters at block +0x0C. These offsets describe distinct objects, not one flat struct.

0x543a50 calls that search, then applies runtime FloatParameter type registration checks. If the first matching name has the wrong type, it returns null; it does not search later duplicates for a compatible type.

Three original rebinding windows call that same typed lookup and store its returned pointer:

- Base Track weight: 0x5a2636..0x5a2651, destination +0x0C.
- KeyBlendTrack control: 0x5a2773..0x5a278e, destination +0x40.
- ReferencedTrack control: 0x5a2813..0x5a282e, destination +0x24.

The complete lookup/type-check routines and these windows passed 12 lookup cases and 12 binding cases (Speed, Direction, case variants, null slots, absent names, duplicate names, prefix differences, wrong type). Test containers, string blocks, registration tags and prebuilt temporary strings are explicit synthetic fixtures. Original lookup calls execute; there are no callback/return-value stubs. String construction/destruction and entire cloning/actor setup are outside the windows.

Evidence: validate_pc_parameter_name_binding.py and pc-parameter-name-binding-validation.json.

## FloatParameter source configuration

The source loader at 0x777a70 uses RangeSize, RangeStart and DefaultPhase properties for scalar entries. Static missing-property branches select 1, 0 and -1 respectively. It passes name/phase/start/size to factory 0x54fce0, which allocates a 0x20-byte FloatParameter and appends its pointer to the same container array at +0x94/+0x98. Constructor 0x5a20c0 assigns name and fields, retaining raw phase at +0x1C and invoking the verified normalized setter.

Numeric configuration window 0x5a20cd..0x5a2113 passed 45 cases without stubbing the original setter. Allocation/name assignment are outside that window; callback pointer is null.

The matching grl_bm_walkrun.banm declares empty FloatParameter Speed and Direction blocks. Combining those declarations, static missing-property branches and the verified numeric window gives initial stored/normalized values of zero for both. This is an initialization derivation, not evidence that running-game Speed/Direction stay zero or use an assumed movement-speed formula.

Default-phase/reset virtual method 0x59da50 calls the setter only when stored phase +0x1C is >=0. Its negative default is not simply an extra normalized input for every update. The callback/notification system and live writers still require tracing.

Evidence: pc-walkrun-parameter-default-audit.json, pc-parameter-config-filter-copy-validation.json, parameter loader disassembly.

## Samurai::Filter — constructor and resolver traced

RTTI and constructor writes connect the real Filter vtable to constructor 0x4ce250. Its factory 0x4ce2e0 allocates 0x1C bytes. A dynamic array begins at object +0x0C, with payload pointer +0x10. The constructor's copy window 0x4ce2ad..0x4ce2ca copies count*4 bytes from the source float array through the original native memcpy.

Five native window cases (counts 0,1,3,62,707) preserve source floats and destination guard bytes, including negative values and values >1. No clamping occurs in this copy path. Destination storage is preallocated in the fixtures. This does NOT establish that negative or >1 values are authored, valid at runtime, or preserved by every later operation.

Static chain:

- Source array builder near 0x4fbcf0 reads a named numeric array, pointer and count, then calls cache insertion 0x4fabc0.
- Cache insertion checks existing lookup, invokes Filter factory 0x4ce2e0, then stores the new reference in a name map.
- Runtime lookup 0x4e1790 searches the map at owner +0x0C and returns its referenced object.
- Runtime resolver 0x774500 gets a configuration record, uses the parsed Filter string at record +8 and calls 0x4e1790 through the object reached from resolver +0x20 then +0x0C. It stores the resulting reference at resolver +0x28. Mirror follows a separate lookup and destination +0x4C.

Only payload copying is executed by the new filter test. Source parsing, map construction, lookup and resolver are statically traced, not executed end-to-end. Float array index meaning, length relative to controls, and actual mask application remain unknown. Do not equate the array with 62 bone weights or add it to the viewer on that assumption. CachedMaskFilter was an earlier generic string lead; the confirmed Samurai::Filter RTTI path is now the better target.

## What changed in the viewer

No animation changes. These discoveries constrain a future named parameter registry and filter binding layer, but they do not justify guessing live Speed/Direction, per-control masks, or channel overwrite order. Existing selected-native previews retain their current recorded fixtures and fallbacks.

## Next research targets

1. Follow the caller of the FloatParameter setter/notification path into the identified actor/controller's update. Separate scalar normalized phase, raw stored value and gameplay speed/direction units.
2. Follow reads of resolved Filter +0x10 into clip-buffer processing, then verify its index mapping and multiplication/application order with synthetic fixtures.
3. Resolve source filter arrays and their correspondence with Elsa's connection/port tables. Preserve original names and complete source paths.
4. Validate external-channel/processor precedence before applying source channels currently skipped at computed outputs.

## Capture readiness

We now know the parameter-container layout and name lookup semantics. We still do not have a verified pointer chain from the active Elsa actor to that container. No broad name-scan/hook dump or new Cheat Engine run is requested yet. Once ownership and a per-frame update site are confirmed, use a bounded hotkey-armed read-only capture of actor identity, matching parameter names/values, active clips/times, effective weights, resolved filters and final palette in the same frame.

## Reproduce

- python trace_pc_parameter_binding.py (hash-pinned static regions/RTTI)
- python validate_pc_parameter_name_binding.py
- python validate_pc_parameter_config_filter_copy.py

Both tests execute original code offline with Unicorn and the existing research dependencies. See pc-parameter-binding-filter-manifest.json for 14 disassembly regions and exact byte hashes. The earlier native normalized getter/setter/time-remap tests remain separate evidence.
