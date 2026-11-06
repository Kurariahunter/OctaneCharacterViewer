# Elsa skin-output association checkpoint

Source: original Elsa OCT decoded graph; no importer or prefab changes.

The source AssociationPool explicitly links SkinInfluence palette indices to named world-transform outputs. Matching the terminal type/name against HeaderStrings[HeaderStringIndices[Header-1]] uniquely resolves 45 of 64 associations. The remaining 19 require full header ancestry resolution; they must not be assigned by guessing.

Confirmed unique terminal matches:
- Knee_Left: influence 55, node 432, ConcatenateChainTransform inputs 19 and 13.
- Knee_Right: influence 51, node 461, ConcatenateChainTransform inputs 18 and 13.
- Ankle_Left: influence 54, node 441, ConcatenateDilationTransform inputs 435 and 432.
- Ankle_Right: influence 50, node 470, ConcatenateDilationTransform inputs 464 and 461.
- Hips: influence 56, node 419, ConcatenateDilationTransform inputs 410 and 103.

Stored output values differ substantially from skin bind worlds and must not be interpreted as computed bind transforms. Default evaluation of the knee/ankle paths stops at unsupported InvertConcatenateChainDilation node 420; Hips stops at an unvalidated relationship processor. These are fail-closed results, not bad-pose evidence.

Next: native-test InvertConcatenateChainDilation, identify and validate the additional relationship on the Hips dependency path, then compare computed world outputs against skin bind worlds. Preserve Scale/Unscale metadata throughout before generating any skinned preview. Existing compensated leg fixture remains diagnostic only.

Reproducible inventory: validate_skin_associations.py. Results including attempted evaluator checks: skin-association-validation.json. Terminal-name matching does not independently prove full HeaderLayout ancestry.

## Follow-up: two blocking operators evaluated

InvertConcatenateChainDilation traced through factory 0x4f1600, wrapper 0x4ea6c0, allocation 0x4de320, constructor 0x4ca6c0, vtable 0x1b2efc4, execute 0x4d2370. Two-input native tests: 200 mixed-axis positive uniform-scale cases, maximum matrix error 1.3070345463717103e-6 for inverse(Input0) @ inverse(Input1). Research FootEval now supports it. Nonuniform Transform semantics remain outside this test.

Relationship processor 17 is an anchor-scale relationship, not a hips-specific pose table. Inputs nodes24 and22, blob23, output Dilation4. Native full and staged calls agree exactly for109 fixtures, with zero segment caches and identity output. Neutral scale is1.0001134872436523; do not round it silently. This original quantized table drives global scale. Native harness is native_anchor_relationship.py.

All five knee/ankle/hips paths now evaluate. X-reflecting source world matrices substantially reduces bind comparisons: ankles max matrix error .0001343155 and translation distance .0000160621; knees max matrix error .02519185 and translation distance .01043467; hips translation distance .00090202. These are default evaluated pose versus mesh bind pose, not a proof they should be identical. Coordinate reflection must be retained consistently. Knee residual and actual nonuniform-scale propagation still require investigation. No skinned preview or production importer change yet. Full results skin-output-followup-validation.json.

## Native leg skin preview completed

Research evaluator evaluate_native_skin.py now preserves original Transform payloads through the actual knee/ankle skin paths. Newly traced processor executes: InvertTransform0x4d1a60, ConcatenateChainTransform0x57e240, ConcatenateDilationTransform0x57cb30, ConcatenateTransformDilation0x4d0c50. Original constructors/vtables traced from registered factories. Existing native unit fixtures are reused; graph results below corroborate the specific Elsa paths, not arbitrary runtime loading.

Default evaluated knees differ from bind by about1cm. Substituting the authored stored upper/knee locals reduces maximum bind matrix difference to0.000849884. This supports distinguishing IK default pose from bind; no bind-relative rotation correction was applied. Retained original native IK output.

The earlier flattened evaluator made passive ankle-orientation data nonorthogonal. Reading native quaternion components through the Dilation/Transform conversions removes that artifact. Native UnitRotor offset order preserved. Real source output paths, without the earlier manual child-Unscale fixture, now reach original clip targets: active127frames/254ankles maxworlderror7.67518297414536e-7; passive186frames/372ankles maxworlderror9.548831781930068e-7. Hips/knees/ankles/ball/toe world transforms exported. Dilation/control dependencies still use bounded FootEval; full original graph loader/blending not executed.

Unity parent-relative matrices for the passive knee/ankle chain contain shear up to0.04746766 because the source carries independent scale metadata. Individual world matrices are TRS-compatible. A separate research preview therefore uses64 independent palette bones, retains original weights/inverse binds, and bakes world transforms to local curves under a common identity skeleton. The rest of the mesh follows the existing bounded torso preview; arms/face/skirt control decoding is incomplete. This is not a general retargetable rig.

Build and verify scripts: sample_skin_controls.py, validate_native_skin_clips.py, build_native_skin_preview_data.py, DI3ElsaNativeSkinPreview.cs. Evidence reports: native-skin-default-validation.json, native-skin-clip-validation.json, native-skin-export-validation.json, native-skin-delivery-validation.json.

Isolated Unity6000.5.8f1 validation passed. Bind mesh deformation error1.816246e-7; saved clip matrix reconstruction errors active4.768372e-7/passive4.172325e-7. Max skinned displacement active0.06352764/passive0.2114231. Both saved Animator instances move. Visual render inspected at2sec: passive feet remain down during body lean; undecoded skirt visibly follows older partial pose and requires further work.

Live output: Assets/ElsaNativeSkinResearch/NativeSkinDiagnostic/Elsa_NativeSkinComparison.prefab. Active/passive .anim files and controllers beside it. New editor menu: Tools/DI3 Static Converter/Research/Create Elsa Native Skin Preview. Delivered materials use existing reviewed URP counterparts; references checked against live project GUIDs. No production importer or prior prefabs replaced. Research textures still depend on Editor/Data and are not player-build-packaged.

Next useful decoding target: skirt/lower-dress proxy outputs, then arm channels. Rebuilding a conventional hierarchy requires representing native scale compensation rather than collapsing helpers or applying guessed bind corrections.
