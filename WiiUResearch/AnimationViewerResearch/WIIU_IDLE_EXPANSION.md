# Wii U Elsa idle expansion — 2026-10-24

Launch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd and choose a clip in the animation dropdown. It now prefers the separate WiiUIdleExpansion build and wiiu-elsa-idles-full.json.

Available: original specific01 (153 poses), specific03 (152), active idle (127), passive idle (186), active-to-passive transition (56). Each has 64 source-evaluated outputs. The transition is played alone, not through a reconstructed state machine; it need not loop seamlessly. Dress behavior remains parked and unchanged.

Source: EngineFormatResearch/PackageValidation/fro_elsa.zip, read-only extraction using copied existing DisneyInfinityArchive/Asset readers. Each OCT is parsed with the existing BinaryTup parser and its ClipDataBlock extracted. The generalized port reader rebuilds timed/static descriptors for each clip against the same actual source graph. Curve/endian and supported opcode gates remain enforced. The sampler retains the original SHA gate when invoked without an explicit path; explicit paths undergo structural/descriptor validation instead.

Specific02 is excluded: its curve fails the existing continuity validation. That is an unsupported decoder assumption, not proof of corrupt game data. No check was removed to force it through. No universal Wii U character/clip support is claimed.

bake_wiiu_clip.py reuses SourceDressEval and PC native numerical helpers, applies controls/finger preparation, evaluates every source palette association and advances all three dynamic chains chronologically. 120 phase-zero warmup ticks, nominal60Hz physics and PC gravity fixture remain; collision and actor layer scheduling are absent. Original idle rebake agrees within 2.5331974029541016e-7 per matrix component across all 64 outputs/153 samples. Original cached clip is preserved unchanged as pack entry1.

Validation: all new palettes checked finite, positive nonsingular determinant, affine last row, 64 outputs and source association equality. New viewer build has zero warnings/errors. Native WPF smoke loads and skins every clip individually with nonzero motion; reports and endpoint screenshots are in ClipExpansion. Specific03 endpoint inspected. This is implementation verification, not live Wii U parity.

Reproduce individual bake:
python WiiUResearch/AnimationViewerResearch/bake_wiiu_clip.py <extracted.oct.clipdata>

Layout acceptance is in ClipExpansion/clip-layout-audit.json; pack validation and original baseline comparison are adjacent. Source hashes are recorded there and in the pack clip_sources. A generic animation picker already existed; the viewer now prefers this five-clip Wii U pack and updates sample-count/coverage text when switching.
