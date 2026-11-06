# PC run source composition checkpoint

The standalone viewer remains raw, without visual hand corrections. This checkpoint validates source declarations and records unresolved runtime state. Native pose samples are unchanged.

## Confirmed from matching PC assets

- Elsa BENT WALKRUN entry points to characters/class_girl/motions/grl_bm_walkrun.banm.
- The textual graph has Speed/Direction parameters and18 ordered direction groups: nine walk, nine run, including repeated forward entries at the direction seam.
- Speed keys are0.25 and0.5; direction keys are0,0.12,0.25,0.38,0.5,0.63,0.75,0.88,1. These are source parameter values; normalization and in-game interpolation have not been verified here.
- Forward run order: grl_bm_runf.oct, grl_bm_run_upbody_add.oct, human_bm_runf_lean_add.oct. Only lean explicitly sets BlendMethod1. All three omit Weight.
- WALKRUN has no explicit Filter in this BENT entry; this does not exclude inherited/channel/runtime filtering.
- Matching BENT contains88 filter references covering31 names. These are names, not decoded per-control coefficients.

## Verified executable behavior

- Base track constructor field-initialization window0x5a2260..0x5a228f initializes mode+8=0, expression+0xC=null, constant weight+0x10=1, time offset+0x14=0. Stops before nested member construction.
- Original constant-weight getter0x59d500 returns the stored weight when expression pointer is null; six test values from-1 to2 match exactly. Expression-backed weights are outside this test.
- Group evaluator0x5a1590 calls that getter before child evaluation and clip-buffer dispatch. Existing source-mode dispatch tests still describe a bounded pre-evaluated buffer setup.
- Exact Filter property string is at0x1b4c3c0. A direct code reference at0x77cf3b lies in parser0x77cef0; surrounding instructions read an accepted string payload and assign a string member at destination+8 via helper0x41c570. This is filter-name loading, not filter resolution or application. The pointed-to filter coefficient loader remains unresolved.

## Pipeline changes

- Added bounded text declaration parser, independent of the tuple decoder binary path. Unsupported escapes/tokens, incomplete blocks and nonfinite values reject explicitly.
- Added source-composition audit. The current native braid bake validates the exact forward reference sequence before evaluating, and embeds source hashes/declarations and known fixture assumptions in the output.
- Regression confirms all existing clip samples are byte-equivalent under canonical JSON hashing. No runtime weights, filter coefficients or hand offsets were guessed into the output.

## Remaining substitutions to replace

1. Passive idle currently initializes controls before run. Verify actual active base/channel inputs and default-data loading rather than assuming this is the game sequence.
2. Capture identified Elsa active clip/time, Speed/Direction, effective weights and filter identity in the same frame as the skin palette.
3. Trace filter-name resolution to actual per-control/channel coefficients and verify how masks are applied.
4. Trace expression-backed weight evaluation0x59d3c0 and source clip phase/motion-rate use. BENT metadata RunMotionRate7.5/WalkMotionRate2.0 is not directly interpreted as a playback multiplier.
5. Preserve exact typed state, feedback and collision inputs for dynamics.

No new Cheat Engine run requested yet. A filter loader/name hook would fire mainly during loading and would not establish active per-frame behavior; do not repeat that earlier capture mismatch.

## Filter names in matching BENT

- CarryRArm
- CarryRArm_Run_Class_Vio
- CarryRArm_Zero
- CarryRArm_Zero_Run
- CarryRHand
- CarrySpecial_Groot
- CarryUnderArm
- Carry_DinnerPlate
- ChargeRun
- HeadTurn
- HeavyOverhead
- HeavyOverhead_Run
- JP_Throw
- JP_Throw_Marvel
- LightsaberRHand
- RightHandOnly
- Sticky
- StiffRightArm
- Upperbody
- WandFire_Class_Vio
- WeaponBothArms
- WeaponBothHands
- WeaponFireBothArms_Marvel
- WeaponFireRightArm
- WeaponFireRightArm_Class_Vio
- WeaponFireRightArm_Marvel
- WeaponRightArm
- WeaponRightArm_Class_Vio
- WeaponRightArm_EquipNone
- WeaponRightArm_Marvel
- WeaponRightHand

## Follow-up: normalized parameter verified

See PC_EXE_NORMALIZED_PARAMETER_HANDOFF.md. The prior expression-backed terminology is narrowed: native 0x59d3c0 is a normalized scalar accessor, with getter/delegation, setter and clip-time remap tests now passing. Binding actual actor parameters and resolved masks remains unverified; existing previews are unchanged.


## Follow-up: named parameter binding and Filter object

PC_PARAMETER_BINDING_FILTER_HANDOFF.md records verified FloatParameter name lookup and rebinding for weights, key blends and referenced clips, plus source-default and Filter object discoveries. This replaces earlier unknown generic-expression terminology. Filter coefficient indexing/application and live actor updates remain unresolved; viewer poses unchanged.
