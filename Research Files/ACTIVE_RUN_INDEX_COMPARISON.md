# Active running index palette comparison — 2026-10-20

User confirmed Elsa was running during this bridge sample. `compare_active_running_index.py` captured each hand's Hand, Index1, Index2 and relationship-local outputs in one bounded memory read. All five node evaluation stamps agree within each hand. The two hands are separate snapshots, not an atomic full-character frame.

Both first/second local index quaternions match the current viewer's native forward-run diagnostic **exactly**, allowing antipodal quaternion equivalence. This is a local pose signature, not a motion-time or clip-controller identity proof.

Active GeometryNode skin matrices, expressed relative to each Hand matrix, match all 19 saved run sample palettes closely:

| Side | Best maximum component error | Worst maximum component error |
| --- | --- | --- |
| Right | 4.9002e-6 | 4.9433e-6 |
| Left | 5.0770e-6 | 5.1908e-6 |

This comparison follows the active scene slots and hash-verified hand relationship chains established in ACTIVE_INDEX_SKIN_INSTANCE_FOUND.md. It avoids the inactive load-bound identity matrices and the idle-versus-run mismatch seen in an earlier bridge read.

For a geometry-level diagnostic, the actual game index matrices were rebased onto the viewer Hand transforms and substituted for only the four index palette entries. The same viewer mesh, bind poses, weights and remaining palette were retained. Across 19 poses, maximum vertex displacement is 5.7900e-6 model units; selected hand displacement is 5.3337e-6, approximately **0.0121 pixels** in the enlarged comparison. This is not a game screenshot or GPU vertex-output comparison.

Conclusion: there is no measured index local-rotation or active skin-matrix mismatch large enough to explain a clearly visible index-finger problem in the tested forward-run pose. Do not add a bend/spread correction to make this validated path disagree with the game. The unresolved visual concern now needs the actual game skinning/rendering interpretation or a better matched view/pose; no specific alternative cause has been established.

No viewer baseline pose change was made in this step. `live-index-matrix-diagnostic.json` is a separately labelled diagnostic and is not the startup cache.

Artifacts:

- `ControllerState/active-index-coherent-snapshot.json` and `active-index-preview-state-comparison.json` show the earlier non-running sample; do not compare it as a run.
- `ControllerState/active-run-index-palette-comparison.json` is the confirmed running sample.
- `NativePreviews/live-index-matrix-diagnostic.json` and `active-index-palette-comparison.png/json` contain the rebased geometry diagnostic.

Bridge READ/search workflow is live-verified. No new manual CE capture was needed. Addresses remain session-specific; revalidate slots, RTTI, graph aliases and stamps after reload.
