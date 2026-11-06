# Active scene index skin instance found — 2026-10-20

The CE read-only bridge successfully completed live READ, RTTI and exact-byte SCAN requests against PID 67612. It bypasses no permissions: requests are serviced by the user's already-attached CE. No memory writes, injected code, breakpoints or game function execution were used.

The previously captured 62-influence object `0x1EC94960` has Renderer::GeometryNode RTTI, but its candidate hand matrices remain identity payloads with zero evaluation stamps. An exact 62-influence header-layout search over **0x1E000000–0x1F000000** found another candidate at `0x1EBBD720`. It also has GeometryNode RTTI and a complete 62-entry matrix-node table. Search skipped 786432 unreadable bytes; it is not an exhaustive process search.

The second object's hand matrix evaluation stamps advance. A single bounded read per hand captured Hand, Index1 and Index2 matrices with equal stamps within each hand: 60528 on the right and 60584 on the left. These are separate per-hand snapshots, not a globally atomic frame. The first object's inactive/template interpretation remains a hypothesis; the difference in evaluation activity is observed.

Direct pointer-chain checks establish:

| Side | Scene Index1 matrix | Scene Index2 matrix | Relationship | File processor |
| --- | --- | --- | --- | --- |
| Right | 1EBA7C38 | 1EBA7E98 | 1EBB8890 | 171 |
| Left | 1EBA71E8 | 1EBA7D78 | 1EBB8718 | 165 |

For each hand, the Index1 matrix converter input is produced from relationship output slot 0 and the same Hand world node used by its scene Hand matrix. Index2's world Dilation producer reads relationship output slot 1 and the Index1 world converter. Both full 836-byte relationship hashes match the installed PC rig's known hand relationship hashes. Source bone ordering and active table indices agree with these graph roles, strengthening the earlier candidate name assignments.

This establishes the active scene skin-slot → matrix converter → hand world/local graph connection. It is stronger than merely replaying anonymous operators, but does not inspect GPU draw-time palette upload or prove full game visual parity. **No index pose fix was made.** Next compare these actual active palette nodes against viewer output under a comparable pose, preserving per-hand stamps and avoiding idle/run mismatches.

Artifacts in `ElsaSceneResearch/ControllerState`:

- `bridge-initial-reads.json`, `bridge-scene-reference-reads.json`
- `geometry-62-layout-search.json` (complete within the bounded readable range)
- `active-geometry-candidate.json`
- `active-index-skin-snapshot.json`
- `active-index-scene-rig-links.json`

`geometry-vtable-search.json` is a separate broad search that hit the 256-match cap; it must not be presented as exhaustive. Individual bridge requests/results also remain in `OctaneLiveInspector/ReadOnlyBridge/result_*.json`.

All addresses are session-specific and must be revalidated after scene reload or process restart. Bridge expires 15 minutes after starting; F10 stops it. No further one-shot CE script was needed for these discoveries.
