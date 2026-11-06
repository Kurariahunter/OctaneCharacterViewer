> Update: the previously excluded motion is now enabled after independent native-output validation. See [NATIVE_ANKLE_VALIDATION.md](NATIVE_ANKLE_VALIDATION.md). The text below records the earlier checkpoint.

# Backward walking and next turns — 2026-10-22

Restart with Launch_Viewer.cmd and click **Backward walks**. The pack contains **Backward walk** and **Backward-right walk**, selectable through the existing dropdown. Both have0.800000011920929s duration,49 simulation frames,25 saved samples and62/62 source-evaluated palette bones. Prior run packs are preserved. The user visually approved all three backward run previews before this work.

## Source composition

The pinned grl_bm_walkrun.banm groups Walk Back / Walk Right Back declare main walk, grl_bm_walk_upbody_add and the corresponding human_bm_run[b/rb]_lean_add. Lean has explicit Weight0.5 and BlendMethod1. Main/upper absent weights retain the existing bounded unit-weight fixture. evaluate_native_clip.py now enables native main/upper/lean composition for the newly grouped walk profiles, using the declared half lean weight. Previously supported walkf remains on its existing path; existing run weights remain1 unless the source explicitly specifies otherwise.

Straight backward walking's shared backward lean targets six leaf Dilation controls, including source spine nodes252/256; the profile-specific allowlist was extended after type/port inspection. Unknown targets still fail. BENT WALKRUN configuration, motion and companion hashes are checked. No channel defaults, root motion, mirror behavior or automatic direction selection was invented.

The native composition regression checks pass, including a new half-weight lean quaternion case. Existing run composition arithmetic is unchanged when lean weight defaults to1. Forward and backward run previews were not regenerated solely for this opt-in grouped-walk extension.

## Passed bakes

* native-walkb-full-palette.json: max endpoint error1.8532765674468056e-6; max native matrix error2.5331974029541016e-7.
* native-walkrb-full-palette.json: max endpoint error2.4857186199700684e-6; max native matrix error2.60770320892334e-7.

Both pass existing shear/dress checks. build_backward_walk_pack.py validates hashes, group declarations, finite62-bone sample coverage and the explicit0.5 native lean layer before generating NativePreviews/backward-walk-pack.json and backward-walk-pack-validation.json.

## Excluded backward-left walk

The candidate grl_bm_walklb fails the unchanged endpoint invariant at frame31, ankle450, error1.17618116268e-5 versus1e-5 limit. It was reproduced once with an exact error diagnostic. No tolerance was loosened and no successful output was generated. Its profile was removed from the selectable catalog, and it is excluded from the pack. This small residual does not by itself identify the cause or imply a visible problem. Further numerical/graph investigation is parked while expanding other animations.

## Viewer

Launch_Viewer.cmd prefers bin/BackwardWalkPreview. The build passes with zero warnings/errors. The hidden --backward-walk-pack-smoke-test checks the shortcut, two-clip load,62-bone source coverage and pose rendering, plus the existing mesh/import self-tests. These are software checks, not human game-parity confirmation.

## Turning inventory

The pinned PC Elsa BENT explicitly references TURN45L/R -> grl_bm_turn45l/r.oct, TURN90L/R -> grl_bm_turn90l/r.oct and TURN180L/R -> grl_bm_turn180l/r.oct in characters/class_girl/motions. Full alias inventory is ElsaSceneResearch/ControllerState/next-motion-alias-inventory.json. These ordinary turn targets are distinct from hoverboard, rail and weapon-turn tracks. They are identified but not yet extracted, profiled or enabled here.

Next extract those exact six references, inspect their source timing/state and root/graph channels, then enable bounded turning playback without treating character yaw as an arbitrary camera correction. Fingers remain parked.
