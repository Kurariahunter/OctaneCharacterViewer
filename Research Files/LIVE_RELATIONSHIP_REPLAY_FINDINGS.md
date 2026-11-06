# Live relationship replay — 2026-10-19

Capture: ce_relationshippose_20261019_211400_78099671.jsonl. The capture stops normally at 64 events: 32 entries and 32 matching normal exits. No rejected or orphaned pairs.

## Direct native agreement

All full relationship blob hashes match the extracted Elsa hand/thumb records. Input/output node identities, type vtables, widths, counts and selector zero validate. There are eight pairs each for file processors 165 (left hand), 171 (right hand), 173 (left thumb), and 175 (right thumb). Every captured exit input has matching node/metadata stamps.

Replaying the original native evaluator with exit input values and entry initial outputs reproduces every output component exactly: **32/32 calls, maximum error 0**. This is live evaluator evidence, beyond previous synthetic tooling tests. It remains relationship-local evidence, not actor identity, downstream world-transform or final skinning parity.

## Extracted idle source agreement

All 14 inputs also exactly match the extracted elsa_bm_idle_active clip sampled at phase zero:

| Relationship | Input vector in serialized attribute order |
|---|---|
| Left hand | [1.4, .7, -4.9, -10.5, -.6, -21.4] |
| Right hand | [1.4, .4, -18, -17.1, 0, -12] |
| Left thumb | [-7.4] |
| Right thumb | [-12.6] |

Values above are rounded for reading; JSON retains exact float32 numbers. Using the file-derived input values and serialized rig output initialization, rather than captured entry initial outputs, still reproduces all 32 live outputs with **maximum error 0**. Thus the source scalar pattern, relationship bytes, and bounded rig-initialized evaluation agree for this captured idle state. No unique actor/source identity is inferred merely from a pattern match.

## Consequence

Do not add finger offsets or alter idle relationship decoding to compensate for the remaining visual problem: the tested local outputs already agree with the game. Investigate unchecked operations after the relationship output, control-to-world transforms and skinning, or run-specific source composition if the deformation occurs during running. This result does not validate the -46.9/-14.9 run-source pattern or any other motion.

Next follow the ten relationship-local output nodes into the final skin matrices and compare that stage independently. Prior hierarchy audit checked only selected two-input Dilation operators; listed unchecked nodes and matrix conversion paths remain candidates. Preserve this zero-error checkpoint before extending the evaluator.

## Artifacts/reproduction

- ElsaSceneResearch/analyze_relationship_pose_capture.py: pair/hash/type validation and native replay.
- ElsaSceneResearch/ControllerState/live-relationship-pose-analysis.json: full captured/replayed values.
- ElsaSceneResearch/compare_live_relationships_to_idle.py: extracted idle/rig comparison.
- ElsaSceneResearch/ControllerState/live-idle-relationship-comparison.json: 32 source-driven comparisons.

No pose arithmetic, source values, hierarchy or renderer behavior changed during this analysis. No further capture is needed to begin the downstream static audit.
