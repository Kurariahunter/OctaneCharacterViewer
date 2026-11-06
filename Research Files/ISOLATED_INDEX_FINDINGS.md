# Isolated-scene index captures — 2026-10-20 evening

Inputs:

- `ce_isolatedindex_20261020_212119_164937781.jsonl`
- `ce_isolatedindex_20261020_212225_165003468.jsonl`
- `ce_isolatedindex_20261020_212250_165028484.jsonl`

All end at the time limit. There are 114 hash-identified hand relationship snapshots in total, 684 observed scalar links, 228 world Transform observations and 228 second-joint matrix observations. Each matrix observation checks the world Dilation operator and its matrix conversion. All replayed downstream values match exactly, with maximum component error zero and no rejected records. Scalar links match node, producer, bytes and fresh stamps; world/matrix predecessor continuity also passes.

All recorded scalar contributions identify controller `0x09233280` and candidate owner name `characters/biped/biped.ct`. This is one **observed contributing controller for these hand records**, not proof that only one controller exists in the process. The name identifies a generic biped class, not Elsa's actor or renderer. User supplied scene isolation (only Elsa, both mounts removed) strengthens the context but does not replace renderer identity proof.

The first capture holds constant hand values. For the right hand, index inputs are approximately [7.184765, 0.4, -12.790541]; for the left approximately [6.651522, 0.7, 0.385007]. Do not assign an animation name solely from these values.

The second and third captures vary between non-running hand values and the known forward-run input pattern: bend controls -46.900001525878906 with spread controls zero on both hands. This pattern agrees with the viewer's current running controls. There is therefore no evidence here that a simple incorrect running bend scalar explains the visible index issue. The captured idle/run time transitions are not synchronized to a video or independent actor scheduler.

Next work should address renderer/palette consumption or a more precise visible pose discrepancy, not repeat scalar or operator validation. Current evidence does not authorize arbitrary index offsets or a claim of full game visual parity. The separately corrected thumb offset remains a distinct issue.

Reproduce with `analyze_isolated_index_capture.py` and the three input paths. Reports are `ControllerState/isolated-index-ce_isolatedindex_*.json`. No new viewer pose changes in this step.
