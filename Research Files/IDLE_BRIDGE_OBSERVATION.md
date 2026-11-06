# Idle bridge observation — 2026-10-20

Read-only bridge PID 67612 responded. Revalidated both relationship blob SHA256s via processor+0x58 -> relationship+0x3c -> 836 bytes, and membership of all four index matrix nodes in the 62-entry geometry table. Initial direct processor-byte hashes were not the relationship blob; corrected pointer traversal matches both pinned files.

65-second capture: 172 snapshots per hand, all internally equal evaluation stamps, 172 distinct stamps per hand. However, only ONE unique world index pose per hand throughout the capture. No idle break movement was observed in these selected nodes. Nearest specific-idle sample errors: right .00862, left .05857, NOT parity. Nearest pose is not clip identification. This could be paused/unfocused gameplay or inactive/incorrect instance; not resolved by stamp advancement alone. User asked to confirm visible game animation/focus before another capture. No viewer or decoder correction made.

Artifacts: ControllerState/live-idle-index-observations.json, live-idle-index-summary.json. Reusable bounded sampler sample_idle_index_bridge.py retains provenance guards, data-only bridge reads and best-effort completion beep. Address validity must be rechecked each session.
