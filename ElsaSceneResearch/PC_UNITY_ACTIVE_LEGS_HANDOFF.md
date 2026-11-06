# Installed-PC active-idle hip and leg preview — 2026-10-17

Open Assets/DI3PCLegsPreview/Generated/Elsa_PC_Legs_Preview.unity and press Play. One active-idle Elsa, 27 animated weighted bones, 127 samples at 30 Hz. The existing arms/head/torso previews and original rig/materials are preserved. This is a bounded research preview, not a universal animation importer.

## Reproducible offline path

Run bake_pc_legs.py with the existing research Python runtime. It freshly reads the hash-pinned PC model and original active idle OCT. No live capture values are used in the bake. evaluate_pc_legs.py combines the bounded upper-body graph with the PC-specific relationship blobs and 8-input/3-output IK execute 0x5382f0. native_pc_relationship.py executes the original file-provided blobs. No old downloaded Elsa model or 13/4 solver is loaded.

Native solver input slots: StartPosition, MidPosition, EndPosition, Target, PoleVector, optional rotor (null in observed PC instances), Twist, external scalar (1 for this bounded preview). Source Axis is a Vector, not a rotor; the supported configuration is explicitly restricted to the observed [1,0,0] Vector/null runtime-slot case. Arbitrary factories/global scales remain unsupported.

The synthetic numeric solver adapter is exactly equal to the header-preserving replay in 120 previously connected PC solver cases. This validates the adapter, not the entire upstream graph or clip identity. pc-file-ik-adapter-validation.json records it.

## Transform details

Native Transform payload: quaternion[4], translation[3], uniform, Scale[4], Unscale[4]. It is not a flattened affine matrix. Native compose copies Scale.w into uniform and forces Unscale.w to 1. native_pc_transform_scale.py and evaluate_pc_raw_transform.py preserve the fields through native operations, rather than recovering rotations from a sheared matrix. Native compose, point, concatenate fixtures pass 500 checks (max error 3.43e-7). ShrinkingVolumeScaleZ execute 0x4c8b40 was traced from registry factory 0x4e8780, constructor 0x4c8b00, vtable 0x1b2e3f4.

The weighted rig has no separate Thigh or Ankle bones. Knee includes source Thigh @ Knee; Ball includes source Ankle @ Ball. Cached neutral chains match weighted bind pivots within floating-point precision; the existing sub-millimeter Hips and Spine1 pivot offsets are preserved. Do not add guessed bone names or calibrate away the authored rotations.

## Validation and limits

Active idle: both ankle targets checked on every frame (254 endpoint checks); maximum residual 3.3469560540157614e-07 source units. Unity local matrices match baked data within 8.94e-7. Saved Animator knee motion measured 0.536682 degrees at 40% of the clip; 189 curve bindings (27 bones × 7). Scene-floor contact and the original game's layer blending are not verified. Fingers, facial motion and dress simulation are incomplete. Dress/helper hierarchy remains the prior preview setup.

## Passive stretch is deliberately excluded

At passive idle time 0, left PC IK returns stretch 1.0301345587. Simply multiplying affine transforms overshoots the target by 0.01277555; native Transform concatenation produces a different 0.01159350 residual. Both naive hierarchy products are insufficient to establish the original rendered skin/length-compensation path. Do not suppress this failure or label the passive feet planted. pc-passive-leg-stretch-open-issue.json saves the exact inputs, outputs and residuals. Next: trace ScaleConnection and the runtime skin hierarchy's scale/unscale propagation, then validate the passive endpoint and skin mapping before enabling it.

## Files

- bake_pc_legs.py, evaluate_pc_legs.py, evaluate_pc_raw_transform.py
- native_pc_relationship.py, native_pc_transform_scale.py, native_pc_lean_ik.py
- pc-legs-animation.json, pc-legs-bake-validation.json
- pc-file-ik-adapter-validation.json, pc-transform-scale-native-validation.json
- pc-passive-leg-stretch-open-issue.json
- Unity builder: Assets/DI3PCLegsPreview/Editor/DI3PCLegsPreview.cs
- Existing previews remain unchanged. Builder refuses overwriting its Generated folder.
