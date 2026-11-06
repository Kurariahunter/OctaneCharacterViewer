# Head-group mesh diagnostic — 2026-10-24

The default preview mode now carries the source-authored Head subtree together. PreviewRig exports its parent indices from the file's Basis hierarchy. A checked ancestor walk selects Head, BrowLeft, BrowCenter, BrowRight, CornerLipLeft, CornerLipRight, Jaw, LowerLip, UpperLip, hair01 and hairStart. Missing hierarchy links are not guessed. Eyelids remain selected from their explicit skin associations.

The carried influences use headWorld @ inverse(headBindWorld), preserving each influence's bind-relative offset. The four eyelids use their individually evaluated world skin matrices. This is a deliberately hybrid diagnostic: brows, jaw and hair do not yet have individually evaluated local animation. No production playback or complete head graph is claimed. Body/neck and excluded hair boundaries can still reveal partial-palette seams.

All 5,419 source vertices retain normalized weights. The carried head influences plus eyelids affect 2,480 vertices. The remaining 2,939 remain exactly unchanged at all three snapshots. Head-relative and absolute-lid-only modes remain available for comparison. Focus eyelids, reset, orbit and zoom remain available.

Validation: exporter succeeds with 5,419 source normals and weighted vertices; Python finite/weight/unchanged-region assertions pass. check-preview.cjs passes 12 mode/frame combinations and focus/reset/orbit/zoom handlers with a canvas stub. This checks script execution, not visual correctness. Automated browser visual inspection remains unavailable because local file URLs were blocked; no workaround was attempted.

Open eyelid-preview.html locally. Next useful check is to inspect the middle snapshot in Head-group and Head-relative modes, then expand source evaluation beyond the four lids. Production OctaneCharacterViewer remains unchanged.
