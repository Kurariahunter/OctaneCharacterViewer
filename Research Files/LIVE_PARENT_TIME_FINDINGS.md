# Live parent time findings — 2026-10-20 00:01

Capture ce_parenttime_20261020_000119_88138781.jsonl completed at the ten-second limit. Twelve parent entries and18 child-call observations: six single-child, six left-child, six right-child. Raw hits:2418 parent entries,1510 single,908 left,908 right. First-six-entry quota per parent bounds coverage.

All18 observed child times AND normalized parent times match original5A1630 arithmetic exactly. No rejected links. Analyzer checks parent/context/stack,selected child pointer and stable child duration. Example incoming0.3999999761581421,parentduration0.6000000238418579 normalizes to0.6666666269302368 and maps to childtime0.4000000059604645. Equal durations do not imply bitwise identity of input/output due to float32 division/multiplication. This exact rounding is now live-verified. All accepted durations in this capture are0.6000000238; unequal/zero durations remain covered only by earlier bounded synthetic fixtures.

Six single-child calls link to nested KeyBlend entries at pointer09437DC0 using selected-child pointer, stack minus4 return-address delta, ordered sequence and identical incoming time bytes. This joins parent-to-child time propagation across the two runtime nodes in one capture; it is not a thread identity or final blended buffer proof.

Reports: ControllerState/live-parent-time-analysis.json and live-parent-time-nested-links.json. Combined checkpoints remain separately scoped: file sampling, child blend, selector and parent time now have exact bounded live matches. Next stage is capture the parent-specific two-child blend destination (sites5A16EE/5A1740 and their returns), then final controller/rig routing. No viewer pose changes or hand offsets.
