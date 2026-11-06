# Live run group source checkpoint — 2026-10-19 22:27

Three captures now expose native ReferencedTrack movement sources through track+0x28 -> asset+0x3C. Source byte candidates and weight/mode/filter arguments are joined within the SAME group-dispatch record, rather than inferred from adjacent events.

-22:27:04: 27 standalone clip samples,57 group dispatches,12 buffer entries;45 group records joined to extracted files.
-22:27:11: 15 standalone clip samples,69 group dispatches,12 buffer entries;57 group records joined.
-22:27:25: 17 standalone clip samples,67 group dispatches,12 buffer entries;55 group records joined.

Matched group sources include grl_bm_runf,runlf,runrf,runl,runr,grl_bm_run_upbody_add and corresponding human run lean tracks. Main direction and upper-body sources use mode1. Forward upper-body references observed at weight1; other upper-body references observed at0.899999976 and0.850000024. Lean tracks use mode0/weight1. All sampled filter pointers null. These are CHILD dispatch factors, not complete inherited KeyBlend weights or full graph output. Directional parent blend coefficients/phase/time still need reconstruction.

Important matcher correction: lean blocks are shorter than256bytes. Previous fixed256 comparison incorrectly excluded them by comparing beyond end of FILE block. Matcher now compares min(filelength,256),minimum32bytes,and records compared_bytes/entire_file_block_covered. Forward lean is120bytes, diagonal lean136bytes; all known file bytes compare exactly with corresponding start of captured memory. Bytes beyond those lengths are ignored and allocation extent is not inferred. Larger sources remain prefix-only candidates, not full live hashes.

This supports the source selection/mode used by the forward-run viewer fixture; it does not establish complete live contributor composition, actor identity, runtime timing, final scalar values or palette parity. No viewer pose changes. Next useful step: join ReferencedTrack local evaluation time and per-row clip-buffer values to these identified movement sources, then compare with file sampling and native dispatch. Do not compensate hand shapes with arbitrary offsets.

Reports: ControllerState/live-run-group-source-joins.json and live-locomotion-source-analysis-222704_82483625.json, -222711_82490312.json, -222725_82504531.json (each with .prefixes.json companion). Existing completion beep remains.
