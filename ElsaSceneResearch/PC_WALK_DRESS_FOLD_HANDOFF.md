# Walking dress audit and source-correct Aim comparison

2026-10-17. The visible dress fold remains unresolved. This increment delivers a justified evaluator correction and a controlled comparison, not a cosmetic clothing repair.

## Delivered comparison

Open C:/Users/Kurar/Disney Reloaded/Assets/DI3PCDressFoldPreview/Generated/Elsa_PC_DressFold_Preview.unity. Both are side views: left is the preceding upper-body walk, right uses prior-output initialization for native dress Aim. Each plays the same four in-place walking cycles and then holds. They should look nearly identical. Older previews and original mesh/weights/bind poses are preserved.

## Real exporter discrepancy corrected

The previous captured closed-loop validation demonstrated that native Aim uses prior orientation state. The graph exporter nevertheless initialized each Aim from identity through DressEval. New FeedbackDressEval resolves particle alignment inputs, initializes Aim from the chain's stored previous local rotor, stores the computed result, and feeds that same native quaternion back to the next particle/Aim update.

The corrected graph evaluator matches all 217 accepted captured local-rotor observations, including 104 carried-state steps, with maximum quaternion component error 0.0. This tests the actual graph adapter against independent captured output, using replay-predicted particle positions and captured anchors. It does not establish full file-control or cloth-collision equivalence.

Across the walking export, this changes only dressLeftStart/dressRightStart palette matrices. Maximum angular changes are about 0.01964/0.01442 degrees. Every other palette matrix remains unchanged. Maximum original-mesh vertex displacement is 0.0001434827482746931 model units. The correction is therefore too small to explain the large visible folds.

## Correct PC mesh audit

Original converted PC mesh data was read in isolated Unity: 5,419 vertices, 8,935 triangles, 62 bone names/inverse binds. CPU linear blend skinning uses those exact weights and matrices; no old downloaded-model research data was used. Original weight sums pass tolerance. There are 200 dress-dominant vertices and 404 valid adjacent dress-face edges in the diagnostic mask.

The metric is the increase in adjacent-face normal angle relative to bind geometry. It measures sharp folds, not full collision or self-intersection. The worst observed edge at time about 1.4 seconds is between vertices 5352/5362, triangles 8845/8846, with about 178.35 degrees of additional folding. Vertex 5352 blends dressRightStart/dressLeftStart about 50.2/49.8 percent; vertex 5362 about 90.2/9.8 percent. These are original weights. This localizes an affected hem region; it does not prove the weights are incorrect.

Two deliberately nonphysical CPU counterfactuals isolate causes:

- Removing lower-chain flex while retaining upper-dress motion and bind-relative attachment still produces about 160.16 degrees at the worst sample.
- Making all four dress bones rigid relative to Body reduces that fold metric to about 4.30 degrees, but would let the legs penetrate a stationary garment.

Neither counterfactual is native reset or a proposed fix. Neither is delivered as an animation. The results show the fold depends on broader dress/leg-driven deformation, rather than solely the tiny Aim initialization discrepancy. They do not diagnose one unique attachment or skinning error.

## Reference limitation and next evidence

The existing Research_20261016_194811_253384.mp4 game recording was inspected at coarse intervals; it shows idle/reference poses and camera movement, not a usable side-on walking comparison. No original-game walking parity claim can be made from it.

Next obtain an original-game side-view walk reference and compare the garment drivers, attachment/bind-to-palette mapping, possible missing character layers and actual skinning behavior during that same gait. Lower-chain capsule count was zero in the accepted captures; arbitrary capsules, weight edits or smoothing have not been introduced as a claimed source fix.

## Validation and files

The corrected bake retains ankle/matrix/dress invariants. Isolated Unity comparison build, saved Animators, finite skin and six rendered poses pass; inspected stills retain the visible folds. Fresh saved scene references original materials. GUID references resolve. Temporary CPU render helper and mesh-audit helper were not delivered to the user's project.

Canonical files under F:/DisneyInfinityPortalTest/ElsaSceneResearch:

- evaluate_pc_feedback_dress.py; bake_pc_feedback_walk.py.
- validate_pc_feedback_evaluator.py; pc-feedback-evaluator-validation.json.
- pc-feedback-walk-animation.json; pc-feedback-walk-validation.json; pc-feedback-walk-comparison.json.
- pc-original-skin-mesh-audit.json; audit_pc_walk_dress_folds.py; pc-walk-dress-fold-audit.json.
- pc-dress-fold-comparison-animation.json; pc-dress-fold-unity.log; pc-dress-fold-render.log; pc-dress-fold-delivery-validation.json.

Reports/scripts are mirrored under C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch. The decoded animation reader remains partial; the unresolved fold is explicitly recorded rather than hidden by altered mesh data.
