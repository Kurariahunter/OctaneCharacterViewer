# PC source skin graph and dress attachment checkpoint — 2026-10-17

## Ready preview

Open `Assets/DI3PCSkinDressPreview/Generated/Elsa_PC_SkinDress_Preview.unity` and press Play. Left = active idle, right = passive idle. Existing DI3PCArmsPreview and DI3PCLegsPreview and the original converted rig/materials are unchanged. This preview uses an independent world-space skin palette; it is not a Humanoid/retargetable rig or a replacement gameplay prefab.

## Movie_017 finding

The earlier local-bone preview held the dress helpers at defaults, with a visible shin-through-hem gap. It also omitted the actual native skin output chains, which matters for PC leg stretch. The new six-pose checks show the dress covering the shin rather than exposing that gap. This is visual evidence for the checked poses, not a proof against all self-intersections.

## Passive stretch resolution for this scope

The earlier 0.01277555 discrepancy came from multiplying local limb affine matrices rather than evaluating the source skin graph. The PC graph obtains Knee-to-AnchorScale through InvertConcatenateChainTransform then InvertTransform. It also composes AnchorScale-to-WorldBasis explicitly. These operations preserve Scale/Unscale compensation differently from simple Unity parent scale multiplication.

Both source PC clips now pass the native ankle endpoint test through those source output paths: active 127 samples, passive 186, 626 leg cases total. Maximum residual 4.36347579401143e-07 in source units. Goals and endpoints are compared in the same AnchorScale basis. The former comparison used local affine products and did not follow this skin path; the older diagnostic remains saved as historical evidence. No manual foot offset, altered target or clamped stretch was used.

Skin nodes are resolved by exact full Association.NodeName -> HeaderLayout path, and checked against InfluenceRefs (all 62 names uniquely mapped). The matrix producer input is a Transform or Dilation. Native Transform point math converts the payload to its actual affine matrix; it is not treated as a flattened matrix. 31 source-driven bones include the earlier upper body/arms/helpers, hips/knees/balls/toes, UpperDress_Left/Right and dressLeftStart/dressRightStart. Remaining 31 bones retain bind offsets following recorded fallback parents; facial and finger controls are not decoded by this change.

## Dress path

Upper dress uses its actual source skin output: source nodes 636/640, with Thigh_OL and proxy groups evaluated. Lower dress uses source DynamicChain processors 550/551, source ChainData and particle bind/config fields, original native reset execute 0x4acad0, source control constraint roots, native difference/inverse-vector/Aim, then original skin output composition (699/715).

This is an independent reset for every sample. No temporal stepping, gravity/collision scene, full constructor/name resolver, or original simulation update order is claimed. The lower dress can look stiffer or more flared than the game; that is the next dynamics task. Original particle source values and bounded runtime fixture defaults are distinguished; constructor scalar slot 0x98 remains 1 in this reset fixture, not a proven dynamic drag assignment.

626 reset-chain checks: root error 0.0, maximum segment-length error 6.183306006102285e-08. Uniform anchor/container requirement and unit particle bind scales are checked explicitly; unsupported configurations fail.

## Newly traced native operators

- TransformTransformWithDilation: registry factory 0x4d7b60 -> allocator 0x4c56c0 -> constructor 0x4b7600 -> vtable 0x1b2cb94 -> execute 0x4d7e90.
- TransformTransformWithTransform: registry factory 0x4d7fe0 -> allocator 0x4c57b0 -> constructor 0x4b7660 -> vtable 0x1b2cbf4 -> execute 0x4d82c0.
- 100 random rigid convention checks against Converter @ Input pass, max error 3.99e-7. Nonuniform payload propagation uses the original native routines, not that unit-scale analytic reference.

## Unity validation

Each preview clone unpacks the original prefab and reparents the existing 62 palette bones directly under the animation root, preserving bind world transforms. Source mesh, vertex weights, inverse bind matrices, UVs, textures and material references remain original. The original source prefab is not edited. Flat palette world matrices avoid introducing Unity parent-scale shear. Remaining inherited bones are baked to world transforms before export.

Ten curves per palette bone (position, quaternion, scale), 620 bindings per clip. Matrix checks on all 313 sampled poses pass: maximum local reconstruction error active 6.03497e-7, passive 1.046807e-6. Saved Animator knee motion is nonzero in both clips. Skin vertices are finite throughout. Largest source world TRS orthogonality residual 1.4127351732887561e-06. Rendering checks six poses, exact skin-bone references and flat palette parenting; still visualization uses direct CPU skinning to avoid batch renderer cache issues. Temporary Standard materials are not saved into the delivered scene. Fresh saved scene references original project materials.

Delivery GUID checks pass for all generated animations/controllers/prefabs/scene; no missing references. Scene-floor contact, seamless full-game layering, facial/finger animation and temporal dress dynamics remain incomplete.

## Reproduction and evidence

Canonical scripts live at `F:/DisneyInfinityPortalTest/ElsaSceneResearch`.

- `bake_pc_skin_dress.py`: fresh hash-pinned PC model and original PC clip controls -> source skin outputs -> independent palette JSON.
- `pc_graph_controls.py`: shared decoded leaf override application.
- `evaluate_pc_dress.py`, `evaluate_pc_raw_transform.py`: native anchor/reset/Aim and raw scale-aware transforms.
- `native_pc_chain_reset.py`: bounded PC source-data reset fixture, no old model import.
- `test_pc_dress_transforms.py`: two new typed operator convention checks.
- `pc-skin-dress-animation.json`, `pc-skin-dress-validation.json`, `pc-dress-typed-transform-validation.json`.
- `pc-skin-dress-unity.log`, `pc-skin-dress-render.log`, `pc-skin-dress-delivery-validation.json`.
- `pc-skin-dress-contact.png`: six checked poses.

Next: validate PC DynamicChain temporal stepping against existing PC capture positions/orientations, especially constructor/runtime particle fields, external forces, container/collision linkage, previous orientation and frame order. Keep reset-only mode as an explicit comparison. Do not replace it with guessed spring motion or describe this as a complete original animation reader.
