> Historical checkpoint. Superseded by NATIVE_DYNAMIC_DRESS_HANDOFF.md. The earlier collision/capsule-parent diagnosis was incorrect: the missing reference is ^.Orientation, and native time stepping now runs.

# Elsa dress research checkpoint

## Delivered preview

Live asset: Assets/ElsaUpperDressResearch/UpperDressDiagnostic/Elsa_UpperDressComparison.prefab. Separate active/passive .anim clips and controllers sit beside it. Editor menu: Tools/DI3 Static Converter/Research/Create Elsa Upper Dress Preview.

Source UpperDress_Left node650 / palette18 and UpperDress_Right node655 / palette17 now replace the old bind-offset-under-hips approximation. Added source controls565,605,663,671 to the bounded original clip sampling. All313frames sample successfully. Exactly four palette bones change versus the previous preview: UpperDress_Left/Right and dressLeftStart/Right (the latter inherit bind offsets under UpperDress in this preview). Legs are unchanged in24 sampled matrix regression checks. This does NOT bake native dynamic lower-dress motion.

Isolated Unity6000.5.8f1 validation passed. Bind mesh error1.816246e-7; active/passive sample reconstruction errors4.768372e-7 /4.172325e-7. Saved Animators both move. Maximum TRS world residual1.540999366461079e-7. Render visually inspected: passive dress no longer tilts with the pelvis as one rigid piece; active hem flares and still needs actual lower-chain simulation. New materials use the reviewed URP counterparts from the previous preview. Old assets unchanged.

## Crucial graph discovery

Lower dress is not just an additional animation channel. Source processors585(left) and587(right) are DynamicChain simulations. The four resulting Position outputs are731/735 and746/750, feeding aim and inverse-transform operators, then native skin outputs dressLeftStart733 and dressRightStart748. A third chain583 drives a different part of the rig via715/719.

Producer discovery previously recognized Output[...] but not DynamicChain Position[...]. evaluate_elsa_head.py now registers these six simulation output nodes and fails closed with unsupported DynamicChain. It must never silently return stored zero vectors for them. Both lower-dress start/end vectors are zero in stored data and are not usable default poses.

Authored lower-chain data nodes971/980: GlobalDamping1, IterationRate300, ContainerExtent(.05,.05,.1). Root particles966/975: flags5, bindlength.01. Tip particles963/972: flags6, relative targetZ.37, length.37. Both have inverse mass1, damping1, natural frequency5.026548385620117. Original anchor outputs660/668; containers738/753. ConstraintPoint[0] is supplied by TransformPositionWithTransform processors586/588, using source local nodes968/977; it is not an unknown stored zero.

## Executable trace

Pinned EXE SHA256f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705.

- DynamicChain registration0x4af06c -> factory0x4aa330 -> allocation wrapper0x4a1ea0 -> node wrapper0x49caf0 -> allocation0x493060 -> constructor0x48f110.
- Vtable0x1b2aacc, execute slot16 =0x4ae360.
- Reset0x4acad0; timestep0x4acdb0; integration0x4a1f90; constraint iterations0x4aaa10; velocity update0x48fea0.
- ChainParticle loader0x49fe90 ->496d10 ->491ac0 ->48e9f0 constructor. Source bind variant begins object+40, variant tag+80; flags+90; runtime scalar slots94,98,9c,a0; constraint length+a4; relative target+a8..b0. Native loader disassembly lists property hash/offset writes, but scalar slot names beyond demonstrated reads still need hash confirmation. Constructor sets94/98/9c/a0 to1.
- DynamicChainData loader0x4a29e0 writes source data at+34 damping,+38 iteration rate,+3c container extent.
- Runtime input0frame,1delta,2previous-frame,3external vector,4chain-data,5anchor,6container,8reset. Per-particle groups start9 with stride5: Particle, reserved/optional slot, ConstraintPoint, Velocity, LastTarget. Output positions are bound separately. Frame/time globals are injected by the factory rather than listed in the source DataNodeRefs.

## Native reset test and precise remaining blocker

native_dynamic_chain_fixture.py executes original reset on two source-like particles for60random rotations/translations and positive uniform scales. Maximum reset-position error1.0115446368308412e-6 against transformed bind offsetsZ.01 andZ.38. Uses zero external force and tagged Dilation binds. This confirms the reset placement in those fixtures only. It does not validate timestep integration, original loading, collision setup, or the provisional particle scalar slot names.

Original timestep reaches native helper0x49a3a0 and faults at0x49a3e7 because the fixture lacks processor+34's cached scene/capsule-parent table. The factory populates this table from scene/name relationships around0x4aa7e9..4aa858. Do not substitute guessed zero vectors or present reset-only motion as simulated cloth. Next: resolve those cached references and their+8 data-node linkage, then validate persistent state/frame stepping and source container constraints. AimConstraintProcessorNode and inverse vector/point operations on dynamic outputs also remain to be integrated.

## Reproduction/evidence

sample_dress_controls.py -> sample_upper_dress_worlds.py -> build_upper_dress_preview_data.py -> DI3ElsaUpperDressPreview.BatchValidate in isolated Unity project.

validate_dress_research.py checks graph ownership, rejects all6uncomputed simulation positions, compares prior/new palettes, and runs24native-leg regression comparisons. native_dynamic_chain_fixture.py regenerates reset evidence and captures timestep failure. Reports: dress-research-validation.json, dynamic-chain-reset-validation.json, native-dress-export-validation.json, upper-dress-delivery-validation.json. Disassembly files dynamic-chain-*.txt and chain-particle-loader-disassembly.txt preserve address evidence.

