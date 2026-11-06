# Targeted live finger input probe

Prepared OctaneLiveInspector/CheatEngine/DI3_FingerInputLogger.lua from the verified clock-producer/blend-return logger. Existing probes are preserved. F8 starts after gameplay is ready, F9 stops. It uses one read-only hardware execute breakpoint at the established normal blend return, no injection, no game-data writes and no forced evaluation. It stops at 120 blend observations or 15 seconds; frequent hits can exhaust the event limit quickly.

For each captured contributor (at most 8 of 64), it resolves these biped source ports through that controller's own PortToLocalIndices, verifies inverse LocalToPortIndices agreement and bounds-checks the source container:

| Label | Port |
|---|---|
| Left Index1 | 483 |
| Right Index1 | 510 |
| Left Thumb2 | 805 |
| Right Thumb2 | 812 |

It records raw four-byte cached payload, candidate RTTI, producer pointer and node/metadata stamps. Only a verified Float RTTI should justify decoding as a float. Unmapped ports or unverified containers are explicit boundaries, never index-zero fallbacks. Payload reads do not trigger evaluation; stamp mismatch means stale cached state may be present.

It also records candidate per-port filter coefficients and existing contributor scalar factors, priority, flags, configuration names/source lineage and mapping snapshots. Filter allocation extent is not independently captured; coefficients remain candidates until checked against known mapping/filter evidence. A matching biped map is not actor identity. These source snapshots do not prove all contributors are active for the target actor or establish complete scalar blend output.

Three real Lua5.3 mock scenarios pass: normal mapping/read/absent-port handling and reload cleanup; signature rejection; breakpoint installation failure. Synthetic data explicitly checks port483 -> local0 -> cached source node and marks other ports absent. Report: CheatEngine/finger-input-logger-mock-validation.json. Mock files are separate from live captures.

## Run

Attach Cheat Engine to DisneyInfinity3.exe, execute DI3_FingerInputLogger.lua in Lua Engine, and use the same Elsa scene. **Start running first, then press F8 while continuing to run**, because 120 blend hits may complete before a later input change. Send ce_fingerinputs_*.jsonl from OctaneLiveInspector/Captures. A separate idle capture can be useful afterward, but one running capture is the immediate comparison needed.

Next analysis will validate typed payloads and mapping, distinguish stale caches, compare run input values against preview (-46.9 index bend, -14.9 thumb bend), and inspect contribution weights. Do not apply hand corrections before that evidence is understood.
