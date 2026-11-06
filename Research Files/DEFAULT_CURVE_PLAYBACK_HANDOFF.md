# Default endpoint/activation playback

`native_default_curve_time.py` implements the verified applied boundary byte 0xF8 for finite, positive ranges with an in-range initial phase. It starts stopped (state byte63=3), activates explicitly, integrates native float32 rate/elapsed-clock arithmetic, clamps on crossing either endpoint, and stops with state byte63=3. Exact endpoint equality remains active until a later crossing. Reverse and zero/negative effective rate cases are tested.

Activation of a frozen state refreshes the cached clock; activation of an already active state retains its cached clock. Activation invalidates the adapter cache even in the same publication. Callback/event delivery and native metadata stamps are not implemented. The pause helper is a bounded state operation, not a tested full native pause callback implementation.

Validation: `ElsaSceneResearch/validate_default_curve_time.py` passes 144 exact native phase/status comparisons and three complete native activation calls (callbacks and metadata pointers null). Tests cover directions, initial endpoints/interior, backward/zero/positive input-clock changes, rates and overshoots. Native phase fixtures execute the time arithmetic window and native endpoint stop helper; frozen output emission remains outside scope.

## Opt-in preview integration

`evaluate_native_clip.py` accepts `--timing native-default`. Existing default `--timing fixture` and the WPF Preview button remain on the established fixture path. Native-default currently requires `--cycles 1`: repeating/reactivating scheduling is not reconstructed.

The opt-in path creates an engine clock, publishes/activates once, advances integer milliseconds on a deterministic approximately-60-Hz schedule, publishes, and requests native default phase. Dynamics receives that tick's native delta seconds after the initial frame. Warmup remains the existing 120-tick reset-pose fixture. Timeline timestamps use integer milliseconds; end time rounds upward to ensure the clip endpoint is reached. This is an explicitly supplied preview schedule, not a recovered OS/game scheduler.

Example from F:/DisneyInfinityPortalTest:

```
python OctaneCharacterViewer/evaluate_native_clip.py "ElsaSceneResearch/InstalledGameAssetCheck/RunMotions/fro_elsa/characters/class_girl/motions/grl_bm_runf.oct" --output "OctaneCharacterViewer/NativePreviews/native-default-run-test.json" --timing native-default
```

The generated test passed all existing transform/IK/dynamics invariants: 37 simulation frames, 19 exported samples, ending at timeline .601 s with source phase .6000000238418579 and stopped state 3. Trace validates strict timestamp progression and token increments. This is an integration/invariant test, not a visual game-parity comparison. Output: NativePreviews/native-default-run-test.json and its .validation.json.

The report includes timing_configuration.mode, applied boundary byte and per-frame phase/token/status trace. This allows inspecting the new path without confusing it with the unchanged fixture. Profile/source graph limitations, absent collisions and unsupported channels still apply.

Next: evaluate the other supported profiles under the opt-in timing path, compare playback visually, and decide on explicit viewer UI exposure. Do not silently turn stopped default clips into looping clips; cyclic 0xAE configuration needs its own verified setup and caller scheduling.
