# PC Elsa run hands and braid-root checkpoint

Open Assets/DI3PCRunHandsPreview/Generated/Elsa_PC_RunHands_Preview.unity and press Play.
Left: previous run plus lean. Right: original native finger relationships plus source hairStart output. Earlier preview assets are preserved.

## Verified changes

The source upper-run clip authors both hands: Index1, Index2, Middle1, Middle2 are -46.9000015; spread controls are zero; Thumb2 is -14.8999996. These are source scalar controls, not manually assigned Unity bone angles. Native RelationshipProcessor 0x54c9a0 evaluates processors 165/171 (six inputs, four outputs each) and 173/175 (one input/output each). The existing mapped thumb-base transforms are also evaluated. Twelve finger/thumb palette bones and hairStart now use source outputs instead of bind-relative fallback, for 44 source-driven bones total.

The original 31 source-driven body/dress matrices match the previous bake exactly (maximum element difference zero). Four cycles, 73 exported samples, existing mesh and weights preserved. Ankle endpoint maximum error remains approximately 1.17e-6. Isolated Unity build and render checks passed; six rendered phases inspected by script, phase 0.1 visually reviewed. The new side view visibly curls the fingers and changes braid-root posture. Exact original-game hand parity still requires user visual confirmation.

## Braid boundary

hairStart is now evaluated through its existing source relationship/constraint path. hair01/hair02 still use bind-relative fallback. The braid uses DynamicChain processor 548, distinct from dress chains 550/551. Its constraint path first reaches unsupported TransformPositionWithTransform node 862. The current native chain adapter explicitly accepts only the two validated dress configurations. Do not simply relabel the braid as a dress chain: its authored particle/chain payloads, constraint transform, type tags and orientation feedback must be checked first. A failed diagnostic can leave evaluator busy state populated; use a fresh evaluator for each independent probe.

## Evidence

pc-finger-native-probe.json: native synthetic scalar sweeps and authored clip controls; not live actor validation.
pc-hand-hair-audit.json: skin output/dependency inventory.
pc-run-hands-regression.json: unchanged body/dress source matrices and added bones.
pc-run-hands-validation.json: bake invariants.
pc-run-hands-unity.log / pc-run-hands-render.log: Unity validation.

Next: validate the braid constraint transform and construct a dedicated native chain-548 fixture using its own source parameters, then test chronological feedback before replacing hair01/hair02 fallback.
