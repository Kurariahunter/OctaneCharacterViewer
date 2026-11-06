# Running index finger: current evidence — 2026-10-22

Recomparison script: compare_latest_run_index_capture.py.

The current full-palette forward-run artifact was compared with the retained coherent historical capture active-run-index-palette-comparison.json. For both hands, captured Hand/Index1/Index2 matrices share a stamp. Comparison uses inverse(Hand) times Index1/Index2, with the same reflection as the preview. Across all19 preview samples, maximum matrix-component residual is4.943343785812626e-6 on the right and5.19082160299611e-6 on the left. The authored finger controls are constant through this run. No synchronized body phase or new live capture is claimed.

Saved report: ControllerState/latest-run-index-capture-comparison.json, with hashes of both inputs. These are matrix-component residuals, not angular or visual errors. Small hand-relative residuals support the existing native transform path for this captured state; they do not establish matching rendered geometry, every runtime pose, or final GPU binding.

Prior audits already establish that the exported62-bone order matches OCT influences, binds differ by a consistent common grounding transform, and a fresh PC VBUF decode matches exported indices and weights exactly. See OctaneCharacterViewer/skin-correspondence-validation.json and ControllerState/fresh-vbuf-weight-audit.json. Those reports do not verify live renderer inputs or native GPU skinning. Repeating the same audits would not close that boundary.

## Fresh comparison requirements

The bridge status present at the start of this turn was dated October21 and referred to PID104600, which was no longer running. Its active flag is not evidence of a current connection. The user said they will start Elsa and re-enable the bridge.

Before reads: validate current PID/process/module header and fresh bridge response. Reacquire geometry table and source associations for the new process; do not reuse prior0x1EBA/0x1EBB addresses. Verify the PC Elsa relationship hashes and62-slot rendered object association before labeling bones. Prefer a coherent snapshot of hand/index/middle matrices plus the active mesh/bind data and relevant producer links. Unchanged stamps/poses or stale associations must not be treated as visible animation evidence.

Next distinguish: (1) actual rendered hand differs despite matching transforms, (2) a different active mesh/bind/pose is being sampled, or (3) the rendered game pose agrees and the apparent difference is camera/detail. No manual index pose offsets or arbitrary weight edits are justified by the current evidence. Fresh renderer/binding evidence remains pending.
