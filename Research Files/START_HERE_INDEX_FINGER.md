# Resume here: index finger remains unresolved

## User priority

The user's primary visible concern is the **index finger**, not the thumb. Weekly usage is low. Keep work focused on a demonstrable visual discrepancy. Do not start another broad capture/verification sequence without identifying the missing evidence it will supply.

## Current result

The index finger's visible pose has **not been fixed**. Earlier numerical and composition changes produced negligible visible index/hand differences. Do not present exact native math comparisons as visual improvements.

A separate thumb omission was fixed: TransformTranslationOrientationConnection ignored its declared RotateOffset. Native execution applies the approximately 180-degree Z offset. The updated viewer visibly changes the thumb, but live-game visual parity remains unconfirmed. The user clarified that the index finger was the main concern.

## Existing evidence: reuse it

- `ce_finalhand_20261020_002459_89558703.jsonl`: 42 final scalar observations across 14 hand/thumb ports. Single source and unit factors; outputs match sources.
- `ce_handchain_20261020_003251_90030046.jsonl`: 336 fresh scalar-to-relationship links and 96 exact native relationship replays, both hands/thumbs.
- `ce_worldchain_20261020_003610_90229843.jsonl`: 73 ordered local/world/Dilation/matrix chains. All 219 downstream native operations exact; predecessor node/producer/bytes/stamps continuous. Index/middle paths only.
- `ControllerState/hand-relative-palette-comparison.json`: 146 comparisons across eight index/middle bones, hand-relative matrices within approximately 7.21e-6 across all sampled viewer poses. Removes hand placement; **not synchronized actor/phase proof**.
- `ControllerState/fresh-vbuf-weight-audit.json`: fresh installed-PC VBUF decode matches all 5419 vertices' indices/weights exactly; positions agree after common grounding offset, residual approximately 8.63e-8.
- Actor identity, synchronized game/viewer pose and actual game-renderer palette consumption are not established by these bounded checks.

Captures are in `F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures`; reports/scripts are in `F:/DisneyInfinityPortalTest/ElsaSceneResearch`.

## Next useful step

Obtain or identify a close-up showing the **specific index-finger difference** in the game and current viewer at comparable pose, side and viewing angle. Prefer existing recordings before asking for a new recording. Establish which model is the game/reference, which hand, and whether the issue is root knuckle spread, bend, second joint or fingertip. User's older reports mention both hands, the index/middle gap, first-knuckle direction and tip angle; these are historical observations, not proof of the current remaining defect.

Then test only the hypothesis suggested by that comparison. If another live capture is necessary, explain which missing value it will distinguish. Existing exact index/middle operations and fresh mesh audits do not need repeating without contradictory evidence.

## Viewer state

Launch `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/Launch_Viewer.cmd`.

Startup prefers `NativePreviews/current-native-run.json`, currently the thumb-offset-corrected run, and falls back to the older cache if absent. Supported native clip profiles remain bounded PC Elsa idle and class_girl forward walk/run. The forward-run group uses original 52-byte buffer blending; passive initializer, scheduling and profile selection remain fixtures, not a complete reconstructed engine.

Latest checks: Release build zero warnings/errors; selected-native and default startup smoke exit zero; full run bake passes; independent C#/NumPy skinning agrees for 3 × 5419 vertices within 4.44e-16. These verify supplied palette application, not game visual parity.

No arbitrary finger offsets should be added to the native baseline. Keep experimental pose adjustments separate and clearly identified if the user requests them.

## Existing reference footage checked
Reviewed contact sheets from Research_20261016_194811_253384.mp4 and Research_20261017_195044_169119.mp4 in C:/Users/Kurar/Videos/DI Research. Both show game footage with Elsa too small to resolve individual index joints reliably; the later video also contains motion/action poses. Contact sheets are in OctaneCharacterViewer/ReferenceFrames. These do not provide a trustworthy matched index close-up. Do not infer a bend/spread correction from these distant views. Next needed evidence: close game/reference image and current viewer image showing the same hand and comparable pose/angle, with the troublesome index joint identified.


## New reference — 2026-10-20 evening
User supplied Research_20261020_201921_222923.mp4 (8 s, 2560x1440) and Screenshot 2026-10-20 201948.png. Recording shows game movement then switches to viewer around the end; screenshot is a clear viewer hand close-up. Extracted 2.5 s game crop at ReferenceFrames/index-game-crop.png. Game fist appears more compact; viewer index appears separated from adjacent finger. This is qualitative silhouette evidence, not a resolved joint-angle comparison: game hand is small and phase/view are not exactly synchronized. Existing rig captures have no independent Elsa rendered-actor identity proof. Next targeted test should establish actual rendered actor/hand association or obtain a higher-detail synchronized hand pose, not merely repeat anonymous scalar/operator comparisons. No index correction made from this evidence.


## Elsa-only captures analyzed
Three ce_isolatedindex captures from 21:21–21:22 pass 684 scalar links and all world/matrix math checks (zero downstream error). One observed hand contributor controller, generic biped owner label; renderer actor identity still not proven. Two captures transition to the same -46.9 bend/zero-spread running values the viewer uses. No evidence for fixing index by substituting a different run scalar. See ISOLATED_INDEX_FINDINGS.md; avoid repeating these checks.


## Active scene skin instance located via bridge
CE bridge works live. Load-time object 1EC94960 hand matrices are unevaluated identities. Bounded search found advancing 62-slot GeometryNode 1EBBD720; both index skin-slot chains trace through expected local/world nodes to full hash-matched hand relationships 171/165. Per-hand Hand/Index1/Index2 snapshots share stamps. See ACTIVE_INDEX_SKIN_INSTANCE_FOUND.md and ControllerState/active-index-* reports. No index pose correction yet. Next compare actual active palette under comparable pose; do not repeat template-node searches or generic scalar/operator tests. Addresses are session-specific and bridge expires after 15 minutes.


## Confirmed live running comparison
User ran Elsa while bridge sampled active skin slots. Per-hand local and skin-node stamps coherent; both index local quaternion pairs exactly match viewer running diagnostics. Active hand-relative skin matrices match all 19 run samples within 5.20e-6. Substituting actual game index matrices into viewer mesh changes enlarged hand only ~0.012 pixels. No substantial decoded pose/palette mismatch found. See ACTIVE_RUN_INDEX_COMPARISON.md. Do not resume more index scalar/operator/palette captures without new evidence; next remaining boundary is actual game rendering/skinning interpretation or matched visual perspective. No baseline index correction applied.

