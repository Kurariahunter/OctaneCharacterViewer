# Disney Infinity animation-system reference leads

Reviewed 2026-10-18. User lead: [Game Anim: Disney Infinity Animation System Breakdowns](https://www.gameanim.com/2016/05/16/disney-infinity-animations/), published2016-05-16. This page collects creator breakdown reels; it is not a binary format specification or source-code release.

## Verified creator descriptions

- [Directional Run Cycles — Paul Mombourquette](https://vimeo.com/166218404): author describes target-facing aim locomotion and weapon poses layered over the run with a feathered filter. This is primary author commentary about system behavior. No file-format offsets, mask encoding or executable implementation are supplied by that description.
- [Horse_GateSequence — Paul Mombourquette](https://vimeo.com/166535892): describes stance, walk, trot, gallop, sprint, jump and sliding-stop sequence; credits riggers Jared Monsen, Joe Cosman and Nate Allison. Useful future gait/transition reference, not evidence of PC Elsa channel mappings.
- [Disney Infinity2.0 Web Swing Mechanic](https://vimeo.com/166218135): another original creator reel linked by Game Anim; version2.0 label matters. Do not assume its internals exactly match3.0 Gold PC.
- [Joe Percival Disney Infinity Mechanics Reel](https://vimeo.com/171242422): indexed creator description says shared vehicle/avatar animation combined physics, procedural behavior and full-body animation, with character-specific customization. Supports investigating a hybrid pipeline. Direct fetch failed on recheck; indexed description was accessible. No frame-level video analysis performed.

## Other retained links

- [ToyBox Mounts and Riders](https://vimeo.com/165705506): linked by Game Anim; player/page could not be fetched. Title/link retained only; do not claim its contents were analyzed.
- [Skywalking With Giants interview](https://gameinformer.com/b/features/archive/2015/05/21/skywalking-with-giants-animating-disney-infinity-3-0): related interview lead with animation department head Gavan Knowlton. Treat as a separate reference to review; this checkpoint does not infer technical internals from its summary.

Access limitation: reviewed accessible page text/creator descriptions. Embedded videos were not played or inspected frame by frame. No remote media was downloaded.

## Local corroboration

Our installed-PC Elsa extraction contains class_girl directional clips grl_bm_runf,runb,runl,runr,runlf,runlb,runrf,runrb under ElsaSceneResearch/InstalledGameAssetCheck/RunMotions/fro_elsa/characters/class_girl/motions. These names support an eight-direction locomotion asset set. They do not establish how the game chooses/blends them.

## Implications for the viewer and decoder — hypotheses and next tests

1. Prioritize original filter/mask loading, channel coverage, layer order and effective weights. Creator commentary confirms filtered layering existed, but not a particular PC binary field interpretation.
2. Compare base directional motion alone against the same motion plus upper-body/weapon layers and record contributing channels. The current viewer's hand-written layer selection is not a substitute for original runtime composition.
3. Obtain an identified-actor capture comparing ordinary forward running with target-facing/aim running. Record active clip identities/times, weights, filter identifiers and final skin palettes. Existing directional video descriptions cannot supply those values.
4. Add layer inspection and source/control provenance to the viewer before claiming complete animation parity. Test another direction and another full clip once the selection path is understood.
5. Do not explain the index-finger or thumb discrepancy as a filter problem yet. It remains a candidate alongside source-pose selection, graph/basis interpretation and skinning; manual visual offsets remain separate.
6. Creator references are useful for intended behavior and cross-checking architecture. They do not decode ClipDataBlock compression, recover constructors, identify ABI/type layouts, prove a native blend equation, or resolve braid feedback on their own.

No decoder code or visual hand values were changed based on these references.
