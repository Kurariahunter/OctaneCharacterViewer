# Live linked finger-world validation — 2026-10-19 21:50

Capture ce_fingerworld_20261019_215028_80287281.jsonl SHA256 recorded in ControllerState/live-finger-world-linked-analysis.json.

Two full relationship blob hashes join to PC hand processors165/171. All94 downstream records pass fresh typed snapshot, provenance and native replay checks with exactly zero component error:32 ConcatenateDilationTransform,31 TransformDilationWithTransform,31 TransformToMatrix. No records rejected. Event cap ends midway through the last chain. Raw hits415/267/388 at downstream sites demonstrate filtering; these are not accepted-record counts.

Relationship deduplication retains node identity across frames; seed payload values are NOT compared to later-frame payloads. Each native replay uses inputs captured at that operator's post-output site. This is a local operator test, not a replay of the entire controller graph or evidence of renderer consumption. No actor/thread identity established. Thumb paths and second-joint Dilation-to-matrix output remain outside capture coverage.

Four corrupted-capture checks correctly fail: wrong payload type, broken source node link, stale stamp, altered output. Viewer pose code unchanged; no hand offsets introduced.

Next: compare viewer-produced finger local/world inputs against matched live controller time/state, and cover final second-joint matrix/palette paths. Do not alter already exact native operators to compensate for upstream composition or downstream hierarchy errors.

## Viewer boundary replay — 2026-10-19
Added audit_live_finger_viewer_math.py. After full capture validation, injects each recorded local Dilation and parent/converter Transform into actual LegEval/NativeSkinEval boundary caches and evaluates source OCT world nodes. All94 cases pass: max affine component error7.62939453125e-6; max packed matrix error1.7881393432617188e-7. This exercises the viewer matrix/rotor round trip and actual native conversion routes; remaining differences are below2e-5. No pose code or offsets changed.

This does not reproduce clip composition or parent-hand production, and does not establish final Dilation-to-matrix/render consumption. The live capture covers94 operator calls, not94 independently composed full poses. Reports: ControllerState/live-finger-viewer-math-audit.json and its .native.json companion. Remaining work should target upstream controller composition and final second-joint matrix binding rather than patching these passing operators.

Static follow-up: source OCT explicitly uses DilationToMatrix4x4VariantProcessor for second joints (205<-206,208<-209,217<-218,220<-221), while first joints use TransformToMatrix4x4VariantProcessor (177<-178,202<-203,211<-212,214<-215). Adjacent EXE routines have different output layouts; do not infer the Dilation variant address from adjacency or reuse packed+0x40 without mapping its factory/vtable.
