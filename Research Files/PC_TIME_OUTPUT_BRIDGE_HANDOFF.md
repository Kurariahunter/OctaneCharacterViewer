# Local-time output reaches the clip-time getter

2026-10-19

All 665 captured contributions have a state output-zero pointer identical to resolved clip processor +0x18. Counts are 322/322, 175/175 and 168/168 across the three logs. This includes captured ClipProcessor and BlendedClipProcessor instances. The snapshot relation is per contribution; it does not establish actor ownership or every possible processor type.

Native emission tail 0x5340DA..0x53411A obtains output zero through the original 0x527F20 getter, updates its metadata stamp, and writes a typed record at node +0x34: local time, lower range, upper range, boundary marker, flags. Sixteen tests cover four time values and four status words. Original ClipProcessor time getter 0x528A70 reads processor +0x18, calls node virtual +0x50, and returns the first float unchanged. The fixture supplies a prebuilt virtual table using actual typed payload getter 0x504030 (returns 0x14-byte payload at node +0x34). This is a synthetic typed-node fixture; no claim is made that its vtable pointer is captured from the game. No function-return stubs are used.

The resulting time is consumed by ClipProcessor update 0x543F40, which calls 0x528A70 and passes its result to curve dispatcher 0x52B720. The inspected dispatcher loads the time into XMM5 and forwards it to the corresponding per-curve native routine, including 0x522CF0. No normalization or frame-rate multiplication occurs in that inspected handoff. This handoff is statically traced, not a new complete dispatcher execution test. Existing file-curve decoding tests remain separate evidence.

Thus the established downstream path is:

input clock -> AnimCurveControlProcessor local-time update -> output-zero record -> ClipProcessor time getter -> native curve dispatcher

The input-clock producer and its units remain unresolved. The existing state headers contain pointers to clock input zero and a second input, saved in captured-clock-input-links.json, but not those nodes' producer headers. Do not label local time as seconds solely because the motion looks plausible or its range resembles clip duration. A future targeted capture can read the two input nodes' producer RTTI if static wiring does not settle this.

Tests: time-output-bridge-validation.json; reproduce ../validate_pc_time_output_bridge.py. Complete sampler, clock producer, BlendedClipProcessor time getter behavior and full-cycle game boundaries were not newly tested. Viewer motion unchanged.
