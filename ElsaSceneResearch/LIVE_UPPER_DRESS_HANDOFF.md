# Live upper-dress correspondence

2026-10-16. Capture octane_20261016_231644_1792207004521971800.json.

## What the new reader established

60samples; complete scan; zero failed chunks. First upstream snapshot has76nodes. Recognized processor execute plus exact output alias validates following node+0x18 producer links for known layouts.24ConcatenateDilationTransform,10ConcatenateChainDilation and2ConcatenateTransformDilation nodes were followed. Unknown execute routines remain explicit boundaries; no arbitrary links were accepted.

Skirt anchor path correspondence (source association based on exact parameter signatures and graph shape):

|Side|Anchor input node(source660/668)|Upper-dress parent candidate(source650/655)|Common anchor(source13)|
|---|---|---|---|
|Left|0x1e073f88|0x1e073cdc|0x1e06759c|
|Right|0x1e0741ec|0x1e073e6c|0x1e06759c|

Both live upper-dress candidates are actual validated outputs of ConcatenateDilationTransform. The first parent relationship exactly matches the source anchor -> upper-dress -> common-anchor pattern. Runtime name/character ownership traversal is still separate.

## Matched passive evidence

Captured common-anchor and upper-dress16-float Transform payloads were converted through the original native point routine to affine matrices. Comparing inverse(common anchor) @ upper-dress removes the global game placement. Source equivalents were evaluated with the corrected native/clip controls for all127active and186passive frames, preserving their source coordinate convention.

For the first captured sample, the nearest passive two-side matrix pose is at source time3.1999999175seconds. Its differences are:
- Left translation7.16082448e-5,rotation0.02734005degrees.
- Right translation4.74019722e-5,rotation0.00960493degrees.

Across all60live samples,39have a nearest passive score below0.01 (score=sum of each side's maximum absolute4x4matrix element difference). Passive median score0.00091144,min0.00004856,max1.51997. Remaining samples do not closely match this bounded passive library; they may involve other clips or layers, but their state is not identified by this test.

No live sample has active score below0.01. Active minimum0.76639,median2.01649,max2.02593. This demonstrates that the captured reference does not match our active pose; it does NOT establish that the active source pose is decoded incorrectly. Do not tune active into passive or claim a bulge fix from this comparison.

The native general concat helper reproduces captured upper-dress raw payloads with maximum element difference0.00021172 across the sampled sides/frames. Reads are non-atomic and world coordinates large; this is a bounded consistency check, not exact synchronized runtime replay.

## Next boundary

Passive upper-dress output now has a concrete live counterpart, complementing the earlier lower-dress Aim match. Next investigate source active stance selection/control inputs and unknown producer boundaries. Recorded execute0x4e84a0 calls0x4dc8c0 and0x4e84b0 calls0x4dca50 with an explicit zero parameter;0x530000 appears to be a tagged-component variant processor. Do not assign operation names or extend traversal without checking input layouts and output aliases. Several live graph dependencies differ from the direct serialized graph (possibly instantiated/optimized runtime graph); equivalent passive output does not imply identical processor topology.

No mesh, weights, Unity preview or production importer changed.

## Reproduction

compare_live_upper_dress.py creates live-upper-dress-comparison.json. summarize_upper_dress_match.py appends all60nearest-source-pose diagnostics. Original capture remains in OctaneLiveInspector/Captures. Raw payload tails on untyped nodes are not interpreted; only known Transform/Dilation representations on validated paths are used. Source candidates/time inferred by nearest pose, not live clip metadata.
