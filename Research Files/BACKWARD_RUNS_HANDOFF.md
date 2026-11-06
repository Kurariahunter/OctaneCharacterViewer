# Three new backward run motions — 2026-10-22

Restart with Launch_Viewer.cmd and click **Backward runs**. This loads NativePreviews/backward-run-pack.json; use the motion dropdown for Backward run, Backward-right run and Backward-left run. Each is one0.6000000238418579-second cycle with19 saved samples, evaluated at60Hz over37 simulation frames. Previous motion files and builds are preserved. This is PC Elsa/class_girl source playback, not general retargeting or automatic direction control.

## Source declarations and decoder changes

Added hash-pinned profiles grl_bm_runb, grl_bm_runrb and grl_bm_runlb with their actual human lean companions and existing upper-run/passive-seed companions. BENT WALKRUN defaults and original grl_bm_walkrun.banm declarations are checked. Groups are Run Back, Run Right Back and Run Left Back. Declared upper-body weights are0.8,0.85,0.85; source order main/upper/lean and existing native blend-mode interpretation are retained. No finger adjustments were made; that investigation is parked.

Straight backward lean contains two additional Dilation targets, source nodes252/256 (Cntrl_Spine2/3). Their port/type/leaf identities were inspected before extending the bounded lean allowlist specifically for grl_bm_runb. The backward diagonals use the existing four lean targets. Unknown lean targets still fail. No missing channels were synthesized beyond existing documented initialization fixtures.

All three bakes pass62/62 source palette, endpoint, native matrix, shear and dress checks. Maximum endpoint errors: backward6.091712544617291e-6, backward-right6.154190929961644e-6, backward-left8.135555549836271e-6. Maximum native matrix component error across the three is2.6263296604156494e-7. These numerical invariants do not establish exact game visuals or root-motion behavior.

## Artifacts and reproduction

NativePreviews/native-runb-full-palette.json, native-runrb-full-palette.json and native-runlb-full-palette.json preserve full per-motion evidence. Adjacent .validation.json files record bake checks. build_backward_run_pack.py verifies source/companion hashes,62-bone finite coverage, sample timing and the actual group weights before producing backward-run-pack.json and backward-run-pack-validation.json.

Reproduce a bake with evaluate_native_clip.py on the corresponding extracted RunMotions/fro_elsa/characters/class_girl/motions/grl_bm_run*.oct, output the matching filename and enable all four --native-*-paths flags as for existing full-palette locomotion.

Viewer build in bin/BackwardPreview passes with zero warnings/errors. Launch_Viewer.cmd prefers this build. A hidden selected-native backward-run smoke test generated and loaded19 samples with62 source-driven /0 fallback. The separate backward-pack smoke test checks the three-clip shortcut/load/pose-render path. It is not a human visual comparison or game-parity test.

## Next motion work

Backward walking has an authored0.5-weight lean companion and needs a proper composition extension rather than merely swapping the main walk filename. Turning and jump/fall/landing assets still require inventory/extraction and source state/group inspection. Do not treat a landing additive track or mounted jump clip as a standalone Elsa jump animation. Prioritize actual additional motions; do not resume index-finger fine-tuning unless the user asks.
