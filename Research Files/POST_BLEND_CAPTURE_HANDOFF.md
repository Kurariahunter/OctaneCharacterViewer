# Paired post-blend capture — 2026-10-19

New logger OctaneLiveInspector/CheatEngine/DI3_PostBlendLogger.lua captures before5A1611 and after5A1616 around the native5A14D0 group dispatch call. Before: ESI ReferencedTrack, ECXmanager,ESPweight/mode/filter. After: ESItrack,EDImanager,ESPadvanced12bytes by callee ret0xC. Pair key includes manager/track/pre-call stack address; ambiguous outstanding entry errors rather than overwritten. Destination frame expected depth-1; actual afterdepth must equal prior depth-1 during offline analysis. No thread identity claimed.

Captures raw52byte source rows and initial destination rows before call, then same destination after call. Only nullfilter and mode0/1,depth1..64,rowcounts<=256,threepairs per track/blob/mode,96records/10seconds. No code injection, game writes, forced evaluation or fixed heap addresses. Existing logger unload, signature/PE32guard, cleanup and completion beep retained.

native_pc_raw_buffer_blend.py executes original5A14D0 using captured raw rows, not logical TRS helper packing. Verifies row extents, supportedmask0x1FF,weight0..1,mode0/1,nullfilter,expectednativebufferpop. Eight synthetic two-row scalar cases (modes0/1,weights0/.5/.85/1) pass;threeinvalidinputsreject.

analyze_post_blend_capture.py checks pair sequence, exact manager/track/stackcleanup, destination frame/pointer/rowextent anddepth, then full-byte native replay. Integer masks and finite float errors also reported, with byte-exact result primary. Four native-generated fixture cases pass:exactpair,wrongstackreject,wrongdestinationreject,alteredoutputdetect. ThreeactualLua5.3 probe cases pass:pairedsnapshot/beep,signaturefailure,second-breakpointinstallfailurecleanup. No live post-blend parity evidence yet.

Run DI3_PostBlendLogger.lua,moveElsa,pressF8,keepmovinguntilbeep,send ce_postblend_*.jsonl. This is a new paired capture, not another source-only test. No viewer pose/composition adjustments.
