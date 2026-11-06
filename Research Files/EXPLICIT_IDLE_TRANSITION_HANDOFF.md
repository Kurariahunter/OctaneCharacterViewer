# File-driven explicit idle finger transition

The native transition sequence now reads the XML state's EaseDuration and runs original duration selection, activation, negative-duration replacement and producer updates. The offline sequence explicitly starts at clock0 with configuration units-1, curve parameter1, no override and no force-zero flag. These are stated fixture inputs, not inferred universal actor defaults.

## Validation

`ElsaSceneResearch/test_explicit_state_transition.py` reads IdleC from the installed shared XML. It replays the earlier captured activation using its recorded initial header, configuration and clock offset, resolves duration from the file's3 units, then advances through both recorded update clocks. Both factor values match exactly without reseeding intermediate headers. A separate19-sample zero-origin timeline is monotonic from0 to1. Missing intermediate game updates and callback effects remain unverified.

The opt-in viewer backend option `--idle-transition-state` requires a unique full XML state path, a matching validated idle clip, one cycle and fixture timing. It rechecks the XML SHA256 and outgoing passive clip profile. Existing default playback is unchanged.

Only the twelve already verified idle Index/Middle scalar controls use the native producer's factor. Their explicit outgoing pose is passive idle at phase0; other channels switch directly to the incoming source. This is not a full-body crossfade, actor scheduler, finger correction or general state-machine implementation. Each evaluation starts fresh; ordinary looping of the baked file will repeat this explicit test transition.

## Prepared preview

Open evaluated animation in the standalone viewer and choose:

`F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-explicit-finger-transition.json`

The303-frame/152-sample bake passes palette, native matrix and dress checks. Against the saved specific03 baseline, three samples change, affecting four left Index/Middle bones. All samples after134ms are identical. The small, brief difference is expected for this partial test; it does not establish visual game parity. No game capture is needed to inspect this result.

Reproduce:

```powershell
& 'C:/Users/Kurar/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'F:/DisneyInfinityPortalTest/OctaneCharacterViewer/evaluate_native_clip.py' 'F:/DisneyInfinityPortalTest/ElsaSceneResearch/InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_specific03.oct' --output 'F:/DisneyInfinityPortalTest/OctaneCharacterViewer/NativePreviews/native-idleC-explicit-finger-transition.json' --idle-transition-state '%FILENAME%/BasicMobility_Group/Idle_Group/Passive_Group/IdleC'
```

Next: extend typed source blending and explicit outgoing/incoming clip timing beyond these twelve controls, validating each supported channel type before claiming a complete native transition.
