# Original walking upper-body tracks added

2026-10-17. New scene: C:/Users/Kurar/Disney Reloaded/Assets/DI3PCUpperWalkPreview/Generated/Elsa_PC_UpperWalk_Preview.unity.

Press Play: front view left, side view right. Four synchronized in-place cycles run for about 3.2 seconds, then hold the last pose. The older walking and idle previews remain intact.

## Source evidence

The original `grl_bm_walkrun.banm` forward-walk group references:

1. `characters/class_girl/motions/grl_bm_walkf.oct`.
2. `characters/class_girl/motions/grl_bm_walk_upbody_add.oct`.
3. `characters/human/motions/human_bm_runf_lean_add.oct`, explicitly BlendMethod 1, Weight 0.5.

The first two referenced tracks have no explicit blend-method or weight field. Their mapped source-node sets are disjoint. The preview combines those original leaf values at matching source phase; it does not invent quaternion blending between overlapping controls or infer semantics solely from the `_add` filename. This is evidence for a scoped reconstruction, not full runtime blend equivalence.

Both source durations are 0.800000011920929 seconds. Upper ClipDataBlock SHA256 is c26a1a02d253b33241c1d255350eaf840390b30da2e2b67c2dae118ee33c174a. Lower SHA256 remains c7cb6ff6c071e31388a7a1840675c070363884c943afda8c9b1abe63b2c859f7. The source audit lists the full forward group and explicit mappings.

The upper clip has 39 control records, including 33 mapped ports. Six ports do not exist in the verified PC Elsa model mapping: 27, 28, 122, 667, 668, 854. They are reported and excluded, not guessed. The separate half-weight lean track is also excluded pending its blending semantics. Remaining controls start from the earlier passive pose where neither selected track supplies a value. Finger controls are present in the source, but the existing fallback finger palette is unchanged.

## Export and verification

`bake_pc_upper_walk.py` now applies the original upper tracks after the disjoint original lower-body tracks, replacing the held arm/torso controls. Native sampling, correct PC source graph, leg IK, scale compensation, gravity dress feedback and verified packed-matrix conversion are retained.

- 126 upper-curve Python/native comparisons pass, including source endpoints. Maximum error: 2.7272450686677274e-08. Unknown curve flags remain rejected.
- Lower-body palette matrices are exactly unchanged across all 97 samples versus the preceding walking preview. Compared bones: Body, Hips, both knees, balls and toes.
- Source upper-body motion is measurable: shoulders about 27/24 degrees, elbows about 35/35 degrees, spine nodes about 5–7 degrees over the cycle.
- 5,211 native matrix/point-affine checks pass; maximum component error 2.5704503059387207e-07.
- 386 ankle checks pass; max endpoint error 2.9889454303198084e-06. Dress root error is zero, maximum segment-length error 7.680211050464791e-08. Warmup checks also pass.
- Unity clip has 620 bindings across 62 palette bones. Matrix reconstruction error is 6.407499e-07; finite skin and saved Animator knee motion checks pass.
- Six poses rendered. Inspected front/side stills show the released hand pose, alternating arms and torso changes. Earlier dress folding/clipping is not resolved by adding upper-body motion.
- Fresh scene retains original materials; temporary render helper was not delivered. All 10 referenced GUIDs resolve.

Output is still a preview palette, not a Humanoid gameplay rig or universal animation reader. Simulation remains 60 Hz with 30 Hz exported poses and 120 initial-pose settling ticks. No gameplay root translation or full actor-layer reconstruction was added.

## Files

Canonical folder: F:/DisneyInfinityPortalTest/ElsaSceneResearch. Scripts and reports are mirrored under C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch.

- `pc-upper-walk-source-audit.json`.
- `bake_pc_upper_walk.py`, `test_pc_upper_walk_file_reader.py`.
- `pc-upper-walk-file-reader-validation.json`, `pc-upper-walk-motion-validation.json`.
- `pc-upper-walk-animation.json`, `pc-upper-walk-validation.json`.
- `pc-upper-walk-unity.log`, `pc-upper-walk-render.log`, `pc-upper-walk-delivery-validation.json`.
- `pc-upper-walk-preview-0.png` through `5.png`.

The delivered Editor builder is under Assets/DI3PCUpperWalkPreview/Editor, with its pose data. Menu: Tools/DI3 Static Converter/Research/Create PC Elsa Upper Walk Preview. Generated output is protected against silent rebuilding.

Next compare the combined motion visually, then investigate the excluded lean track and template ports or the separate dress collision/deformation issue. No additional live capture was needed for this increment.
