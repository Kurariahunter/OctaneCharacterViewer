# Wii U forward locomotion viewer — 2026-10-24

Launch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd. The existing picker now has seven entries: five preserved idle/transition clips plus WiiU_grl_run_forward_composed and WiiU_grl_walk_forward_composed. The launcher prefers the separate WiiULocomotion build and wiiu-elsa-motion-pack-full.json. Original PC launch remains unchanged.

## Source routing and scope

The Wii U fro_elsa.zip contains class_girl locomotion, not Elsa-named forward walk/run files. Its grl_bm_walkrun.banm explicitly lists three tracks per forward group: grl_bm_runf/walkf.oct, the corresponding upper-body track, and human_bm_runf_lean_add.oct. The lean reference has BlendMethod1 and weight0.5for walk, default1for run. The baker parses and checks these exact source declarations before evaluating the composition. Static lean commands are endian-transcoded, bounded by the existing static reader, mapped through actual Wii U ports and authored-path mapping, and applied through the existing original-PC native clip-buffer blend routine.

Passive-idle phase-zero initialization, unit lower/upper assignments and normalized cycle phase are explicit preview fixtures reused from PC research. Runtime actor layering, filters and arbitration are not reconstructed. Thus these are source-composed previews, not proof of identical in-game blending. Hair/dress retain120tickwarmup,60Hzschedule,gravityfixture,noscenecollision. The dress fold issue is parked; no mesh corrections or tuned finger offsets were added.

## Boundary flags and numerical evidence

The new clips contain curve boundary flags2 and0x12. Their payload layout matches flags0 cubic data. inspect_wiiu_clip retains flags0 as its default and refuses approximate samples for admitted nonzero flags. The native sampler explicitly admits only0,2,0x10,0x12, using the existing native curve routine for all values and boundaries; other flags still fail closed. Existing PC source decoder supports precisely these modes.

The four forward lower/upper Wii U curve blocks total65curves. Every curve is byte-identical to the matching PC source curve after field-width endian conversion. All33 native sample times per curve agree exactly. locomotion-native-curve-crosscheck.json records flag distributions and results. This is strong numerical reuse evidence for these curves, not Wii U CPU execution.

Scaled IK controls use only the existing verified644/650 Transform path and original numerical helpers. Missing authored Dilation Data has the same identity/default-field meaning as the existing source/PC evaluators. No source graph globals are modified.

## Verification and reproduction

Run:4cycles,2.400000095s,73render poses. Walk:4cycles,3.200000048s,97poses. Each output palette has64unique source associations, finite affine matrices and positive nonsingular basis determinants. All three native chains advance once per chronological tick with frame stamps/root/segment checks. Build passes with zero warnings/errors. Native WPF smoke checks both new clips with nonzero skinned displacement; endpoint screenshots were inspected. All five previous clip objects are included unchanged.

Scripts:
- ClipExpansion/Program.cs: read-only archive extraction, substring arguments and OCT/BANM support.
- bake_wiiu_locomotion.py run walk: source-declared forward composition and bake.
- validate_wiiu_locomotion_curves.py: per-curve PC equality check.
- build_wiiu_motion_pack.py: palette/timing validation and seven-clip pack assembly.

Reports and screenshots are under ClipExpansion. Wider direction support and another character's graph remain separate next steps. specific02 remains excluded by the preexisting continuity gate.
