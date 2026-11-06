# Native clip loading checkpoint — 2026-10-18

## New controls

- Open evaluated animation: loads a compatible native-evaluated JSON skin palette. Every clip must match the verified PC Elsa model hash and contain 62 finite named matrices per sample, positive duration and strictly increasing sample times. Invalid files leave the previous preview intact.
- Clip dropdown selects among all clips in the loaded file.
- Inspect native clip (.oct): selects an extracted animation OCT, executes the existing decoder and original scalar-curve/Euler routines offline, and writes a channel report in Inspections. It does not replace the displayed pose cache or claim full graph evaluation.
- Source re-evaluation remains the specific Elsa run/braid bake; it is not an evaluator for whichever clip was last inspected.

## Try it

Run Launch_Viewer.cmd. For both native idles, use Open evaluated animation and select F:/DisneyInfinityPortalTest/ElsaSceneResearch/pc-gravity-dress-animation.json. These older caches have their own documented evaluation limits; loading them does not add newer hand/braid improvements. For the existing walk test use pc-walk-animation.json. Source coverage is no longer hardcoded as 46/16 for every cache.

Native inspection fixtures are under ElsaSceneResearch/InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions and RunMotions/fro_elsa/characters/class_girl/motions.

## Verified decoded source channels

- Passive idle: 6.1666665 s, 18 curves, 69/71 ports mapped to Elsa; unresolved 279,280.
- Active idle: 4.1999998 s, 28 curves, 98/108 ports mapped; unresolved 27,28,122,279,667,668,851,852,853,854.
- Forward run lower: 0.60000002 s, 16 curves, 35/35 ports mapped.
- Run upper additive: 0.60000002 s, 12 curves, 32/41 mapped; nine unresolved.

Five time points (start, quarters, end) decoded with finite native scalar/Euler outputs for each. Model OCT and non-OCT input rejected. This is decoder execution, not a new demonstration of end-to-end game animation parity.

## Remaining work

The viewer is still limited to the verified PC Elsa rig. A selectable native clip needs complete rig-graph evaluation, input/default state, layer masks/weights, time semantics and dynamics before it can generate a trustworthy new palette. Direct binary mesh import still needs to replace the one-time Unity export bridge. We will not substitute Mixamo, rename joints, or apply manual hand corrections in this viewer.

Current source-composition checkpoint remains authoritative for unresolved filters, expression-backed weights and active actor capture requirements. No new Cheat Engine run requested for this step.
