# Live idle index follow-up — 2026-10-20

User confirmed visible idle motion. Extended palette inspection found all 62 matrix slots changing on geometry 1EBBD720 and zero changing slots on 1EC94960 (12 sequential observations each). Thus the previously used geometry remains an active instance. Full-palette samples are NOT atomic.

Second 65-second hand capture: 169 internally coherent samples per hand; 88 distinct world index poses each. Right best hand-relative Index1/Index2 error 8.34e-7; left 1.12e-6 against nearest saved specific-idle samples. 141/169 right and 153/169 left observations below 1e-3. This is bounded evidence of compatible index poses, NOT identification of all three played clips, global phase synchronization, full-animation parity or resolution of specific02's historical continuity warning. Different nearest clips/times may share the same finger pose. Hands sampled separately. First static capture preserved as live-idle-index-observations-static.json.

Artifacts: ControllerState/idle-palette-instance-activity.json, live-idle-index-observations.json, live-idle-index-summary.json. No decoder edits or manual pose adjustments made. Next stronger verification would identify active clip/time and compare phase-aligned whole palettes, rather than interpreting nearest finger poses as clip identity.
