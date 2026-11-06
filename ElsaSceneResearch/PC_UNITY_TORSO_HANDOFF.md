# File-only PC torso/shoulder Unity preview

Delivered: C:/Users/Kurar/Disney Reloaded/Assets/DI3PCTorsoPreview/Generated/Elsa_PC_Torso_Preview.unity. Open and press Play; left active, right passive. Two .anim clips, two Animator controllers, two animated model prefabs and one comparison prefab included. Existing head-only preview preserved.

The same verified-PC file-only channel reader and bounded graph now bake ten source local transforms: Body=134, Spine1=139, Spine2=144, Spine3=149, Clavicle_Left=154, Clavicle_Right=179, Shoulder_Spin_Left=158, Shoulder_Spin_Right=183, Neck=457, Head=462. No live captures used.

All neutral rotation matrices agree with inverse-bind local rotations within 2.11805e-7. Spine1 source pivot differs from skin pivot by 0.0008869022 along source Y. Explicit translation-only pivot preservation retains the skin pivot; other pivot adjustments are float-precision scale. No rotation calibration, guessed retargeting or full-body solver added.

bake_pc_torso.py generates pc-torso-animation.json and pc-torso-bake-validation.json. DI3PCTorsoPreview.cs builds the Unity assets from JSON under Assets/DI3PCTorsoPreview/Editor/Data. Editor menu: Tools / DI3 Static Converter / Research / Create PC Elsa File Torso Preview. It selects existing results; building refuses to overwrite Generated. Python regeneration uses existing offline native dependencies and installed-PC extracted files in ElsaSceneResearch.

Unity 6000.5.8f1 isolated validation:
- Active 127 poses, maximum matrix error 5.364418e-7, maximum skinned displacement 0.06352766; saved Animator head angle 4.340669 degrees at 40% duration.
- Passive 186 poses, maximum matrix error 5.364418e-7, maximum skinned displacement 0.2114231; saved Animator head angle 6.119453 degrees.
- All 313 sampled meshes finite; bone locals outside the animated ten preserved.
- Saved Animator playback works. Both looping clips use linear key interpolation and quaternion continuity.
- Scene generation and visual render checks passed. Rendered two poses with temporary built-in materials in the isolated test project; delivered assets retain original PC materials.

Visible scope limits: arm/leg locals held at bind pose, foot planting not solved, Body motion carries the feet, secondary dress/hair and shoulder-helper constraints incomplete, pre-existing eyelid artifacts remain. Shoulder/arm deformation can look incomplete as the torso moves. Preview-only orphan lid/hair02 parenting inherited from head preview; original source rig and materials not modified. This is not full original idle playback or game layer parity.

Next: reconstruct PC arm/limb graph paths and helper constraints, then lower-body IK/foot planting and secondary dynamics. Avoid filling missing motion with fabricated curves.
