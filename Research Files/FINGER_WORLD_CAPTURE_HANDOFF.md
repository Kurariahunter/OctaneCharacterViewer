# Linked finger world/matrix capture

Probe: OctaneLiveInspector/CheatEngine/DI3_FingerWorldLogger.lua. No fixed live heap addresses. It discovers candidate hand relationship output nodes, then follows exact node-pointer links at verified native post-output sites:

| Site | Observed stage | Register/layout |
|---|---|---|
| 0x54CA19 | Completed hand relationship | ESI processor; six inputs/four outputs; full 836-byte candidate blob |
| 0x57CC15 | ConcatenateDilationTransform output | ESI processor; relative two-input/one-output array |
| 0x4D798E | TransformDilationWithTransform output | EDI output node; producer must execute 0x4D78D0 |
| 0x55DAFE | Transform-to-matrix output | ESI output node; producer typed input/output links |

Source PC mappings show Index1/Middle1 world transforms consume corresponding relationship outputs and hand-world transforms; Index2/Middle2 consume the paired local relationship output with the first joint's world transform. Probe verifies the relationship-processor identity and adjacent slot pairing before accepting second-joint outputs. Matrix capture accepts only tagged first-joint world transforms and uses the verified 48-byte packed payload at output+0x40, not +0x34.

Every accepted downstream record captures its actual input(s) and output, node type vtables, producer pointers and metadata stamps. Provenance tags retain seed sequence, relationship processor and output slot. Prefix/count matching only makes a relationship a candidate: full blob hash must be joined offline before assigning source identity. Records can contain stale caches and lack thread/actor identity. Converter output observation is not proof of renderer palette consumption. Late payload mutation must be considered in replay.

The four hardware execute breakpoints are read-only; no code injection, game-data writes, forced evaluation, or broad heap scans. PE32/ASLR/four instruction signatures and an empty breakpoint list are checked before installation. Known older probes unload. F8 begins, F9 stops, 96-event or ten-second limit. Event cap may end midway through a chain; unpaired downstream paths remain boundaries.

Four actual Lua5.3 mock cases pass: linked relationship/world/dilation/matrix graph, bad source link rejection, signature rejection, and partial-install cleanup. The matrix test checks payload offset0x40 and width48. Report: CheatEngine/finger-world-logger-mock-validation.json. These mocks do not establish live links or game-pose parity.

## Run

Execute DI3_FingerWorldLogger.lua in Cheat Engine Lua Engine with Elsa loaded, then press F8 while idle for a baseline. Start movement before F8 for a movement capture; event limits can fill quickly. Send ce_fingerworld_*.jsonl from OctaneLiveInspector/Captures.

This bounded probe covers index/middle paths; thumbs and final Dilation-to-matrix variants are not followed yet. First analyze seed hashes, exact links/types, freshness and original native operator replay. Compare world inputs/outputs before deciding whether the visual discrepancy lies before conversion, during conversion, or after palette export. Existing no-offset preview baseline is unchanged.

## Live capture 2026-10-19 21:44
96 seeds join by full blob SHA256 to PC hand processors165/171 (48 each), two live processors, all960 node snapshots fresh and expected Float/Dilation types. Capture ended at2906ms on event cap with zero downstream records. This does not establish downstream failure or parity. Input values vary on right hand; left remains constant, so do not assume this is the earlier idle baseline.

Probe revision deduplicates seeds by processor for each bounded session while retaining provenance, counts raw breakpoint hits at all four sites, and allows relative arrays at +0x1c (past the four-byte array header) instead of an unverified +0x24 lower bound. Existing four Lua mock checks pass; revised live behavior remains unverified. Next capture distinguishes an unhit native route from a hit rejected by pointer/type filtering. Viewer pose code unchanged.
Report: ElsaSceneResearch/ControllerState/live-finger-world-analysis.json.
