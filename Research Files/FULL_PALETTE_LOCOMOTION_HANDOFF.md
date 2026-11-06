# PC Elsa full-palette forward locomotion — 2026-10-22

In the viewer choose **Open evaluated animation**:

* Walk: `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-walk-full-palette.json`
* Run: `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-run-full-palette.json`

Both opt-in previews evaluate62/62 palette bones with no bind-offset palette fallbacks. They extend the previously supported class_girl forward locomotion profiles on the hash-pinned PC Elsa rig. They do not establish support for other character rigs or arbitrary motions. Startup/default viewer behavior remains unchanged.

## Change and evidence

The16 additional source paths are eight brow/jaw/lip outputs, four eyelids, two eyes and two forearm overlays. Identical baseline/full bakes preserve the existing source clip composition, passive-idle seed and fixed-step timing. The run still uses the previously implemented native three-layer main/upper/lean composition; this step did not change those weights or blend modes. The walk retains its existing composition fixture; native runtime layer scheduling is not newly established.

All16 added bones change from their old bind-offset fallback matrices. Every previously evaluated bone matrix remains exactly identical across all saved samples, including fingers, body, hair and dress. Consequently the known running-index-finger issue is unchanged and is not claimed fixed by palette coverage.

| Motion | Source duration | Simulation frames | Saved samples | Max endpoint error | Max native matrix error |
| --- | ---: | ---: | ---: | ---: | ---: |
| Walk | 0.800000011920929s | 49 | 25 | 3.122261338650673e-6 | 2.384185791015625e-7 |
| Run | 0.6000000238418579s | 37 | 19 | 1.1727965811987406e-6 | 2.980232238769531e-7 |

Both pass existing matrix/shear/dress/endpoint invariants. Maximum matrix-component differences against fallback baselines are0.2798575535416603 for walk and0.057677289991917347 for run. These are differences, not visual or angular accuracy scores.

## Reproduce

Run evaluate_native_clip.py with the supported extracted grl_bm_walkf.oct or grl_bm_runf.oct, choose an output JSON, and append:

```text
--native-facial-paths --native-eyelid-paths --native-eye-paths --native-forearm-paths
```

No idle-transition flags are used for these locomotion bakes. Sources and companions are verified against native-preview-profiles.json. The new flags remain restricted to PC Elsa idle and these two forward locomotion profiles; diagonal/sideways full-palette coverage has not been tested here.

Run `audit_full_palette_walk.py` (walk) or `audit_full_palette_walk.py --motion run`. Reports are NativePreviews/full-palette-walk-audit.json and full-palette-run-audit.json, with per-bake `.validation.json` files. The coverage-baseline JSON artifacts preserve same-run comparison evidence.

## Remaining boundaries

The user visually approved the full-palette specific idles. These new locomotion previews still need visual confirmation.62/62 palette coverage is not full-engine parity: channel defaults, event/state scheduling, actor collision/root movement and secondary-motion context remain bounded fixtures. Unmapped/computed-output channels remain recorded rather than guessed.

Next: inspect the new locomotion previews, then use the improved complete palette for targeted game-versus-viewer comparisons. The running index-finger question still needs evidence about source composition/defaults and actual game pose, rather than manual corrections to this native baseline.
