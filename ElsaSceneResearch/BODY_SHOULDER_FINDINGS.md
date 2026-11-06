# Elsa body and shoulder diagnostic

Extends the corrected torso test, preserving earlier assets. Selected inputs: body207/212, shoulder336/341/368/373, spine219/226/232, neck240 and head246. Clip-local constants are applied before timed channels. Original native curve and Euler routines are reused; output matrices use the independently verified offset multiplication order.

New outputs: Body102, Clavicle_Left126, Clavicle_Right154, Shoulder_Spin_Left131, Shoulder_Spin_Right159. Default rotations match local skin bind matrices within 1.37e-7 for the new outputs. No broad rotation retarget correction is applied. Existing Spine1 pivot reconciliation remains 0.000887 units.

Active idle body matrix changes up to 0.00404; left/right shoulder-spin matrix changes 0.00927/0.00994. Passive body changes up to 0.06628; right shoulder-spin changes 0.02841, while left is constant. Clavicle local matrices are constant in these clips; they inherit spine motion. Matrix spans are numerical diagnostics, not angles or displacement magnitudes.

Unresolved: Shoulder_Left136 and Shoulder_Right164 output default rotations differ from skin bind by approximately 23 degrees. Translation matches. Those upper-arm local outputs are deliberately excluded pending trace of runtime pose/skin composition. Descendant arms inherit shoulder-spin movement, but elbows/hands are not decoded. Do not interpret this as complete arm motion.

Hips410 depends on unsupported TransformDilationWithDilation output502 (input499, converter498). Processor execution must be established from executable before implementing it. Hips and leg local controls remain fixed. Body output is bone-root motion, not Unity root-motion extraction; foot planting is not solved, so sliding or floating may be visible. Facial controls and BENT/additive composition remain incomplete.

Samples: active127 and passive186 at30Hz. See body-mapping-validation.json for mapping errors, constant channels and motion spans. No production importer or original game files changed.
