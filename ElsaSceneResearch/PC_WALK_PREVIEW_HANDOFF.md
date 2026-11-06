# Original PC forward-walk preview

2026-10-17. Delivered as a separate scene; older previews and original model assets are preserved.

## Use

Open C:/Users/Kurar/Disney Reloaded/Assets/DI3PCWalkPreview/Generated/Elsa_PC_Walk_Preview.unity and press Play. Front view is left; side view is right. Both show the same animation: four 0.8-second cycles, about 3.2 seconds total, then hold the final pose. Stop/play restarts.

This is an in-place lower-body walk. Upper-body controls are held at time0 of Elsa's passive idle, including its hand pose. The separate arm-swing/additive and gameplay locomotion layers are not decoded here. No arm motion was invented. Cloth collision and full actor blending remain incomplete.

## Original source and curve support

QuickBMS extracted walking assets from the installed PC fro_elsa.zip into InstalledGameAssetCheck/WalkMotions. The archive includes shared class_girl grl_bm_walkf.oct; no Elsa-specific forward-walk filename was found in the walk-filtered extraction. All its control ports map to the verified PC Elsa model, with no unmapped ports. The clip drives body, hips, feet and foot-roll controls; it has no arm-swing tracks.

- Archive SHA256:281754d26892e285a73c6f0a739698f68adde22a0406e2a8f9ce6816150197a4.
- ClipDataBlock SHA256:c7cb6ff6c071e31388a7a1840675c070363884c943afda8c9b1abe63b2c859f7.
- Source cycle duration:0.800000011920929seconds;16curves.

The original idle parser rejected curve low bits0x12. Native0x522cf0 extracts dimensions from bits10..19 and uses low bits for boundary handling; knot/coefficient layout is unchanged. pc_clip_decoder.py now accepts the observed boundary bits0/0x12 and records them, rejecting unknown patterns. Sampling still uses the original native routine. This does not add general out-of-range Python boundary-mode emulation.

Independent Python/native in-range comparison:96walk curve cases including endpoints, maximum error1.8225321554155016e-06. Unknown flags rejected. Idle regression:276curve cases, maximum error9.230572821650185e-07,12malformed/time rejections. All pass.

## Bake and Unity validation

bake_pc_walk.py uses the native matrix/IK/dress pipeline, repeating source phase four times while preserving chronological simulation state. Sampling is60Hz with30Hz export and120initial-pose warmup ticks. Gravity and particle configuration are unchanged from the verified PC pipeline. Root gameplay translation is not supplied; the source walk is previewed in place.

-97exported poses;62weighted palette bones and620Unity curve bindings.
-5211native packed-matrix/point-affine comparisons pass, max error2.5704503059387207e-07.
-386ankle checks pass; max endpoint error2.9889454303198084e-06.
-386timeline dress checks pass; root error0, max segment-length error7.680211050464791e-08; warmup checks also pass.
-Source ball-position stride range is about0.95012units, with vertical range about0.12863units per foot.
-Unity matrix reconstruction error3.650784e-07; finite skin, maximum skinned displacement0.7381672units; saved Animator knee motion11.79827degrees.
-Six poses rendered; front/side placement visually checked after correcting positions for the preview camera. Visible alternating strides and dress deformation are present. This does not establish cloth collision parity.
-Fresh saved scene uses original materials. Temporary CPU-skinning/render helper was not delivered.10reference GUIDs resolve.

## Files and reproduction

Canonical research: F:/DisneyInfinityPortalTest/ElsaSceneResearch. Reports/scripts are mirrored under C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch.

- bake_pc_walk.py; pc_clip_decoder.py; test_pc_walk_file_reader.py.
- pc-walk-animation.json; pc-walk-validation.json; pc-walk-file-reader-validation.json.
- pc-walk-unity.log; pc-walk-render-final.log; pc-walk-delivery-validation.json.
- pc-walk-preview-0.png through5.png.

The delivered C# builder and pose data live under Assets/DI3PCWalkPreview/Editor. The editor menu is Tools/DI3 Static Converter/Research/Create PC Elsa Walk Preview. Generated output is protected against silent rebuilding. This is a preview palette, not a Humanoid/retargetable gameplay prefab.

Next useful extension is inspect the bundled walk/run BANM and upper-body additive layer semantics before adding original arm swing. A complete universal animation reader and full actor controller remain unfinished.
