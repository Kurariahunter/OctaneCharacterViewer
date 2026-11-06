# Elsa specific idle tests — 2026-10-20

Added pinned profiles for elsa_bm_idle_specific01/02/03. Their original PC BENT entries are IDLE_BREAKA/B/C. Configuration reads the SHA-pinned BENT and rejects explicit layer/filter declarations or filename mismatches. No manual pose corrections. Existing four motions retained; startup bundle now has seven.

All three full 60-Hz bakes pass existing finite-matrix, ankle, shear and dynamics invariants:
- 01: 5.066667 s, 305 frames, 153 samples.
- 02: 6.666667 s, 401 frames, 201 samples.
- 03: 5.033333 s, 303 frames, 152 samples.

Each passed selected-clip WPF smoke and independent C#/NumPy skinning (three poses x 5419 vertices, max 4.44e-16). Three rendered screenshots inspected. Reports and screenshots are NativePreviews/specific0N-*; bakes native-elsa-specific0N.json and .validation.json.

Important: the historical LATEST_FINDINGS.md packed-curve continuity warning for specific02 is NOT cleared by these tests. Current evaluation uses original native scalar/Euler routines and passes rig invariants, but game continuity/visual parity is unverified. This caveat is retained in its bundle source metadata. All clips remain bounded Elsa graph fixtures, with existing fallback bones/dynamics limitations. Animation event metadata (sound/face events) is not executed.

Reopen Launch_Viewer.cmd; select elsa_bm_idle_specific01_NativePreview, 02, or 03. Watch 02 for unexpected snaps. No Yoda changes in this step.
