# Elsa corrected torso/head diagnostic

Drag Elsa_TorsoComparison.prefab into an empty test scene and press Play. It includes a camera and lights. The two individual DIAGNOSTIC prefabs can also be tested separately.

Active and passive idles animate Spine1, Spine2, Spine3, Neck and Head at 30 Hz, combining clip-local constant channels with native timed curves. Passive Spine2/3 are constant by design. Root, hips, arms and facial controls remain at defaults; helper parents remain preview approximations. This is partial animation research, not the complete original idle.

Corrected output nodes: Spine1=108, Spine2=114, Spine3=120, Neck=393, Head=398. BasisRef identifies the coordinate basis, not the driven bone. Earlier head previews incorrectly used Neck=398 and Head=407 and compensated with bind-relative rotations. Those previews are preserved but superseded. The independently verified RIGHT offset multiplication order remains valid.

Source rotations are now used directly. Original skin pivots are retained; Spine1 requires a 0.000887-unit translation reconciliation. This does not establish exact full engine pose fidelity or additive/BENT layering.

Isolated Unity 6000.5.8f1 validation passed: bind reconstruction error 2.58e-7, sampled local matrix error <=2.99e-7, finite skinned vertices, unrelated bone local transforms unchanged, saved-prefab Animator movement verified. Render inspected. Copied material assets converted to URP Lit; live-project compilation/playback still requires Unity refresh.

Tool: Tools > DI3 Static Converter > Research > Create Elsa Torso and Head Preview. It creates a new uniquely named diagnostic folder. Uses existing Assets/DI3ElsaHeadResearch/Editor/Data source mesh and textures. Editor-only research dependencies have not been packaged for player builds.
