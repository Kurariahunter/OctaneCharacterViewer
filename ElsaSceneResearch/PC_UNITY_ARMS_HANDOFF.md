# PC upper-body/arms preview checkpoint

New separate preview folder: Assets/DI3PCArmsPreview/Generated. Open Elsa_PC_Arms_Preview.unity and press Play (active left, passive right). Two file-derived PC .anim clips and Animator controllers, two animated prefabs and comparison prefab. No live captures, new invented motion or gameplay controller.

## Graph expansion

bake_pc_arms.py + evaluate_pc_arms.py extend the ten torso/head outputs with Shoulder_Left/Right 162/187, Elbow_Left/Right 167/192, Hand_Left/Right 172/197, Shoulder_OL_Left/Right 616/619 and Elbow_OL_Left/Right 490/494. Twenty bones, 127 active and 186 passive frames. All 120 needed source nodes audited: no unsupported required static channel opcodes in either PC idle.

TransformTranslationOrientationConnection currently supports the encountered unit-scale inputs only. ConcatenateInverseDilationTransform and ConcatenateChainInverseTransform are evaluated in the source basis. Elbow helper rotation uses original native UnitRotor3dWeightedAverageProcessor execute 0x4d9ed0 -> helper 0x4c6210. Factory chain: 0x4f2d50 -> 0x4ec260 -> 0x4e0060 -> 0x4cc1d0 -> constructor 0x4b9090, vtable 0x1b2d29c. Runtime inputs are two rotors followed by two scalar weights. Both authored weights reference source Float node 33 = 1.0. Native equal-weight blend validated against shortest-hemisphere normalized quaternion sum in 100 random cases, maximum component error 1.17804e-7. Other weights/configurations deliberately rejected.

The shoulder default network pose differs from the mesh inverse-bind pose by about 23 degrees. Raw source rotations retained; no bind-relative corrective rotation imposed. Neutral main-shoulder outputs agree with source cached identity rotation within 7.61e-8. Shoulder helper output follows its source shoulder connection; the cached helper fallback differs slightly and is not treated as an executed output. Elbow/hand/helper pivots checked against source inverse binds; prior explicit sub-millimeter Spine1 pivot preservation remains.

## Important preview construction correction

Initial arm render revealed detached sleeves. Unity logged that Transform.SetParent on linked prefab children was rejected; the attempted helper parenting in earlier head/torso previews was also not actually applied. Thus prior notes describing that parenting as applied need this correction.

Current arm builder unpacks ONLY the temporary cloned preview instance before parenting. Original source rig and materials unchanged. All helper parent assignments are asserted. Four arm-helper parents follow the source converter graph: Shoulder_OL -> Shoulder_Spin, Elbow_OL -> Shoulder (respective side). Orphan eyelid and hair02 bones attach to Head preserving bind world transforms; Thumb2 attaches to Thumb1 preserving bind world transforms as a preview-only hierarchy approximation. Individual finger animation remains incomplete. Rejected/intermediate outputs retained only in the isolated validation workspace, not delivered.

## Validation

Unity 6000.5.8f1 checks all 313 poses, finite skinned vertices, unchanged unrelated local transforms, quaternion continuity and looping. Saved controllers contain 140 transform component curves (20 bones x 7). Saved Animator elbow motion explicitly checked: active 0.4187135 degrees and passive 2.17609 degrees at 40% duration. Sample matrix errors <=5.364418e-7. Visual render and saved scene checks are recorded in pc-arms-render.log; final delivery dependency check in pc-arms-delivery-validation.json.

The active file-derived pose now includes hand-on-hip placement. Visual similarity is not exact clip/time parity with the game. Legs/foot planting, dress dynamics, complete finger/facial animation, further helper constraints and blend-layer playback are not implemented. Old head/torso comparison assets preserved as historical tests.

Next: review this corrected arm preview, then decode lower-body/foot constraints using the verified PC solver family and file inputs. Keep legacy downloaded-asset 13/4 IK work separate.
