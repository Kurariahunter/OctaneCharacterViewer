# Live geometry-copy remap — 2026-10-22

Update: REMAPPED_RUNNING_INDEX_HANDOFF.md records the completed user-confirmed20-second run sample.78 hand snapshots have exact matching run-local values and relative palette residuals below1e-5. The pending comparison described below is superseded by that report; other local poses were retained separately.

Capture ce_skinremap_20261022_223856_342393328.jsonl records124 post-assignment slots, two complete62-influence copies, and an event_limit stop with breakpoints_released=true. Analyzer: analyze_skin_remap_capture.py. Report: ControllerState/skinremap-223856-analysis.json.

Source GeometryNode0x1EF4BC40 copies into0x1EFED3E0 and0x1EFC33B0. All62 source pointers are replaced in both copies. Both destinations share the same62 replacement nodes; this is observed palette sharing, not an error. Registry count is1675 throughout these assignments, compared with zero in an earlier out-of-copy bridge read. This directly validates the prepared native copy/remap probe on a live event; it does not yet establish GPU draw-time consumption.

Fresh live reads show nonzero advancing stamps and nonidentity matrices for all six sampled hand/index matrix nodes, unlike the earlier load-table identity matrices. The current per-hand reads in skinremap-223856-live-index-nodes.json are separate requests and not coherent shared poses; do not compare them as if synchronized.

The candidate index-base local nodes were checked via their actual producer pointers and complete836-byte relationship hashes. Right producer0x1EFE8548 matches PC Elsa processor171; left0x1EFE83D0 matches165. Links are saved in skinremap-223856-live-relationship-links.json. Native downstream alias traversal and GPU palette provenance remain stronger future checks; source-order labels are not universal assumptions for other rigs.

## Next prepared comparison

sample_remapped_index_bridge.py validates both live destination tables still contain the captured62 pointers, validates the local base producer aliases, then reads each hand's matrix/local nodes in one bounded block. It accepts a hand only when all included stamps agree. Left/right observations remain separate. It compares hand-relative index matrices against the current full-palette forward-run reference and records nearest-pose residuals without claiming clip identification.

The user has been asked whether they can keep Elsa running for20seconds. Do not interpret an unanswered request as evidence that the actor is running. No current run comparison is claimed until the sampling file is actually produced and inspected. Live addresses are session-specific and must be rejected if validation fails.

No decoder motion, weights, bind data or finger-angle correction was changed by this capture analysis. The gain is a verified runtime copy boundary and moving palette candidates, narrowing the renderer association question.

## Short current-pose observation

A3-second bridge sampling pass produced9 observations/18 coherent per-hand snapshots, each with advancing stamps. Before sampling,0x1EFED3E0 still matched all62 captured destination pointers. The second geometry copy's table had been cleared and was excluded; requiring both copies to persist was an overly strict diagnostic assumption and was corrected. The sampler now requires at least one complete matching captured table and rejects ambiguous palettes.

Snapshot: ControllerState/remapped-index-current-pose-3s.json. All18 hand blocks have matching hand/index/local stamps. Maximum-component differences from the constant run-finger reference are approximately0.3220 left and1.7140 right. Movement state was not human-confirmed as running for this pass, so these are pose differences, not decoder errors. No running comparison is claimed. The question requesting20seconds of running remains pending.
