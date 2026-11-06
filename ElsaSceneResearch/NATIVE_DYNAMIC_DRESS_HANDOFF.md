# Elsa native DynamicChain dress handoff

## Current result and correction

The prior handoff's claim that processor+0x34 needed a collision/capsule parent was INCORRECT. Reading the actual literal at0x1b2b00c reveals `^.Orientation`. The cached object points via+8 to an orientation data node, read as a quaternion at node+0x34 by0x49a3a0. Capsule constraint arrays are separately described by processor+0x3c/+0x3e. No fake scene/collision pointer was added.

The missing orientation reference is now provided explicitly in the bounded native fixture. Native DynamicChain runs through real time. Full original execute0x4ae360 exactly matches staged reset0x4acad0 / step0x4acdb0 across120moving-anchor frames. Max pinned-root error9.511054812079725e-10; max chain-length error3.218741567723171e-8; tip lag0.004007251933217049. This test holds the cached orientation at identity and uses zero external force.

## Source header hierarchy resolved

HeaderLayout contains(parentHeaderID,childCount) pairs. Each pair assigns the next consecutive child IDs, starting at1; total child counts2108 equals HeaderStringIndices length. Header strings use HeaderID-1 indirection. Full paths now exactly match ALL64skin associations. The previous19unresolved outputs use Dilation payloads inside a header group named Transform; the group name is not the payload type. decode_header_paths.py checks the full hierarchy, cycles and all exact association paths. validate_skin_associations.py now uses complete paths; historical terminal-only results saved separately.

Position731 path=Anchor|dressLeftStart|Transform.Translation|In WorldBasis;735=Anchor|dressLeftEnd|Transform.Translation|In WorldBasis. Right746/750 analogous. Sibling local orientation outputs are724/739. The source factory resolves the relative `^.Orientation` access and the native integrator reads its cached raw quaternion, rather than treating it as a collision position. Full original name-resolution machinery has not been executed; explicit sibling binding is corroborated by paths, type filter and native quaternion reads.

## Additional native math decoded

- AimConstraintProcessorNode: factory54ff50 -> wrapper54ff20 ->54f100 ->54d3c0 -> constructor54a580 ->vtable1b353dc ->execute534380. Runtime input order AlignInput,AlignReference,UpInput,UpReference,Offset(optional),BasisInput(optional). Source lower dress uses only first four.
- Position3dDifferenceProcessor:5503f0 ->5503c0 ->54f580 ->54d870 ->54b000 ->vtable1b359a4 ->52d0e0. Computes To-From.
- InverseTransformPositionWithTransform:4d54e0 ->4c4590 ->4b7040 ->vtable1b2c6f4 ->4d57e0.
- InverseTransformVectorWithTransform:4d43f0 ->4c3da0 ->4b6ec0 ->vtable1b2c56c ->4d46f0.

100mixed-axis / positive uniform scale fixtures passed for all4operators: max errors point5.72797032916128e-7,vector2.3419245265277056e-7,difference1.6530401047987198e-7,Aim1.5634942577280597e-6. Optional aim inputs, degenerate directions and arbitrary nonuniform inverse transforms are unvalidated. A121direction near-alignment sweep with orthogonal up input had max direction error6.63725011233786e-9. Source chains use nonorthogonal up inputs and retain their native aim result, including small residual direction differences; no artificial correction was applied.

## Original clip anchors through native simulation

sample_dynamic_dress.py uses DressEval/native transforms to compute original source anchors660/668 and containers738/753. This additionally required native aim and difference support for the kinematic lower-dress proxies; positions extracted from Transform payloads keep native translation semantics.

For each side: persistent two-particle memory; original full DynamicChain dispatch per frame; explicit source flags5/6, bind lengths.01/.37, inverse mass1, damping1, natural frequency5.026548385620117, authored container extent.05/.05/.1. Runtime scalar slot98 retains original constructor default1. Native loader offsets and force reads were inspected; not a universal property-hash decoder.

After simulation, native inverse vector/point and native Aim produce local lower-dress poses. Native ConcatenateDilationTransform combines these with each anchor, yielding skin-world outputs corresponding to733/748. Previous frame's computed local aim is supplied to cached orientation at the next step. This is an explicit feedback order, supported by the native cached direct read; complete engine scheduling is not claimed.

Active127frames, passive186frames, total626side/frame samples:
- pinned root errors0 in both clips;
- max chain-length error active7.960102466064711e-8,passive7.221670444979011e-8;
- max skin-origin errors active1.1035681294371986e-7,passive1.156641147752108e-7;
- native skin axis versus simulated chain direction residual active0.00048203131221399875,passive0.0004540347215426876 (under0.028degrees). Preserve native aim; exact parallelism to both nonorthogonal alignment/up requests is not imposed.

Only dressLeftStart and dressRightStart differ from the prior upper-dress bake. All other palette transforms are exactly preserved in delivered data. Original mesh weights and bind matrices retained.64independent palette bones avoid Unity parent-relative shear.

## Delivered assets and tests

Live prefab: Assets/ElsaDynamicDressResearch/DynamicDressDiagnostic/Elsa_DynamicDressComparison.prefab. Active/passive .anim and controllers beside it. Editor menu Tools/DI3 Static Converter/Research/Create Elsa Dynamic Dress Preview.

Built and validated in isolated Unity6000.5.8f1: bind mesh error1.816246e-7; sample reconstruction active4.768372e-7/passive4.172325e-7; saved Animator instances both move. World TRS residual2.4625407298547146e-7. Render inspected at2seconds: active skirt no longer has the previous broad rigid flare. Reviewed URP material counterparts used in live project; all18referenced non-built-in GUIDs resolve. Previous previews and production importer unchanged.

## Limits and next validation

This is a BOUNDED NATIVE SIMULATION bake, not a full game-runtime reproduction. External force explicitly zero. Each clip resets its chain at the start; seamless looping is not guaranteed. Name resolver / complete graph loader / all engine scheduling not executed. Hair, arms, face and remaining authored controls are incomplete. Research texture dependencies remain under Editor/Data and are not packaged for player builds.

Next useful validation: watch the new preview through loop boundaries; check source/global external-force defaults and spring property hashes; test consistent state across a clip transition. The same DynamicChain appears on hair and may be the next reusable target, but do not extend it without inspecting its particle settings and references.

## Files and reproduction

Working research directory F:/DisneyInfinityPortalTest/ElsaSceneResearch. Tools/ExecutableResearch/DressResearch contains checkpoint copies, not a standalone installation of all Python dependencies/model files.

- decode_header_paths.py / header-path-validation.json
- native_dress_math.py / dress-native-math-validation.json
- native_dynamic_chain_fixture.py / validate_dynamic_chain_step.py / dynamic-chain-step-validation.json
- evaluate_dress.py / sample_dynamic_dress.py / native-dynamic-dress-samples.json
- build_dynamic_dress_preview_data.py / native-dynamic-dress-export-validation.json
- DI3ElsaDynamicDressPreview.cs / dynamic-dress-unity.log / dynamic-dress-delivery-validation.json

Run sampler, then build data, then DI3ElsaDynamicDressPreview.BatchValidate in the isolated Unity project. Prior lower-dress unsupported result and reset-only tests remain historical evidence; this handoff supersedes their missing-collision-parent interpretation.
