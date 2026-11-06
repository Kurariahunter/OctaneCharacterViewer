# Remapped live running index comparison — 2026-10-22

The user confirmed **Running now** immediately before a20-second bridge sample. The read-only sampler completed and beeped after saving. No CE execution hooks or game writes were added for this sample.

Saved immutable observation copy: ControllerState/remapped-index-running-20s.json. Analyzer: analyze_remapped_run_index.py. Report: ControllerState/remapped-running-index-analysis.json. The report hashes its live and preview inputs.

## Validated association and sampling

The captured destination table of GeometryNode0x1EFED3E0 still matched all62 remapped pointers before sampling. The other copied object's table had been cleared and was excluded. Index-base producer aliases had been validated against the exact left/right PC Elsa relationship blobs. Each hand's Hand/Index1/Index2/Local1/Local2 values were read in one bounded block. A hand is accepted only when all five stamps agree.

52 observations produced104 coherent hand snapshots, with52 distinct stamps per side. Hands were sampled separately, not as a simultaneous full-body frame. This associates observations with an actual surviving geometry-copy table, but still does not prove final GPU draw consumption.

## Matching run-pose result

Local reference values are taken from the current full-palette run artifact's native finger diagnostics, not fitted to the live sample. Quaternion-sign equivalence is allowed; the matching-local tolerance is2e-6. Actual matching-local error was exactly0 on both sides.

| Side | Coherent hand samples | Exact run-local matches | Matching locals with palette residual <1e-5 | Largest matching-local palette residual |
| --- | ---: | ---: | ---: | ---: |
| Left | 52 | 40 | 40 | 8.13490118689586e-6 |
| Right | 52 | 38 | 38 | 7.498050696108649e-6 |

Palette comparison uses inverse(Hand) times Index1/Index2 against the current file-driven run preview, with the established reflection. Residuals are matrix-component differences, not angular or rendered-image errors. Large world translations may amplify float32 cancellation in the relative calculation; no specific numerical cause is asserted.

The12 other left-hand samples and14 other right-hand samples have different local index payloads. They remain in the report. Every sample matching the run's local values also matches the relative palette within1e-5. Therefore the larger residuals in this session are associated with changed local poses, not an observed failure to compose the matching run pose. Their exact clip/state identity was not captured; do not label all of them a particular transition or animation.

## What this changes

We now have stronger evidence than native operator tests alone:78 live hand snapshots from a verified surviving post-remap geometry table match the decoded run-local values exactly and the relative index palette closely. This sample shows no index decoding/composition discrepancy for that matching run pose. It does not establish all finger states, source mesh identity at the GPU, rendering equivalence, or full-engine parity.

Do not introduce the earlier manual knuckle/spread/tip adjustments as native decoder fixes. The visible concern should next be investigated with a matched camera/pose comparison of game and viewer, and—if the discrepancy persists—the actual draw-time skinning inputs/equation and mesh association. No further identical relationship capture is justified by this result alone.
