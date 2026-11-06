# Playable file-only PC head/neck Unity preview

Delivered in C:/Users/Kurar/Disney Reloaded/Assets/DI3PCIdlePreview/Generated.
Open Elsa_PC_Idle_Preview.unity and press Play: active on the left, passive on the right. Individual .anim, .controller and model preview .prefab assets are also included. The comparison prefab includes camera and lights for an empty test scene.

These two reproducible clips derive entirely from the verified installed-PC model and active/passive idle OCT files. No live capture data is used. Head and neck move; all other bones remain in bind pose. This is not a full original idle or general animation importer.

Pipeline: read_pc_idle_files.py -> bake_pc_head_neck.py -> pc-head-neck-animation.json -> DI3PCIdlePreview.cs -> native Unity animation clips/controllers/prefabs and test scene. JSON data is supplied under Assets/DI3PCIdlePreview/Editor/Data. The editor menu Tools / DI3 Static Converter / Research / Create PC Elsa File Idle Preview selects the generated prefab when present and can build when Generated is absent. Native source dependencies remain in ElsaSceneResearch for offline rebaking.

Key PC graph discovery: DilationTranslationOrientationConnection factory 0x4f4040 -> 0x4ecfd0 -> 0x4e0ca0 -> 0x4ccef0 -> constructor 0x4ba220, vtable 0x1b2d9cc, execute 0x4e84a0 (helper 0x4dc8c0). DilationOrientationConnection factory 0x4f3d40 -> 0x4ecd90 -> 0x4e0ae0 -> 0x4ccd10 -> constructor 0x4ba070, vtable 0x1b2d89c, execute 0x4e84b0 (helper 0x4dca50). Rotation-only uses Input, RotateOffset; translation+orientation uses Input, optional TranslateOffset, RotateOffset. Native variant routines require an explicit Dilation runtime type fixture; treating them as simple copies ignores the rotation offsets.

Bounded PC head evaluator supports the encountered unit-scale head/neck dependencies; unsupported operations fail. Output node 457 = Neck local to Spine3, node 462 = Head local to Neck. Native connection offsets make neutral graph outputs agree with source inverse-bind local transforms: maximum component error 1.89296e-8 Neck, 1.78814e-7 Head. No bind-relative corrective pose was applied.

Unity 6000.5.8f1 validation in isolated project:
- Active: 127 samples; maximum clip sample matrix error 1.192093e-7; maximum skinned displacement 0.04378669; saved Animator head angle at 40% of clip 4.340669 degrees.
- Passive: 186 samples; maximum clip sample matrix error 1.788139e-7; maximum skinned displacement 0.1289464; saved Animator head angle 6.119453 degrees.
- All sampled mesh vertices finite; unrelated local bone transforms unchanged.
- Both saved prefab Animators actually animate; loopTime enabled; quaternion continuity and linear key interpolation used.
- Rendered and inspected two sampled poses. Minimal validation project temporarily used built-in materials for rendering only; delivered assets reference original PC materials.

Preview-only helper approximation: imported orphan eyelid and hair02 bones reparented to Head while preserving bind world transforms, on cloned preview prefabs only. Original rig asset unchanged. Existing eyelid geometry/constraint limitations remain visible; no facial animation or helper-constraint reconstruction claimed.

No production source mesh, rig, materials or current user scene replaced. No full body, base-layer mixing, gameplay, dress simulation or general retargeting support claimed. Next step: expand file-only graph evaluation to torso/shoulders, then remaining limbs and original procedural state.
