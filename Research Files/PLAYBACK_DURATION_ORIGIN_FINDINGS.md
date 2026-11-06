# Upstream replacement duration — 2026-10-21

The negative-duration fallback is supplied by the playback request, rather than calculated inside the TransitionProcessor.

## Confirmed argument path

- Common playback method788EB0 receives replacement duration as its fourth argument. After source selection succeeds, its window788F20..788F60 forwards that value as controller770210's fifth argument.
- Controller770210's ending guard770364..77038C reads that fifth argument and uses it only if controller+64's existing duration is negative. Setter525CB0 stores the value.
- Wrappers789A00 and789A40 forward their fourth argument unchanged to788EB0. They differ in the preceding source-selection helper. No default duration is assigned in these forwarding windows.
- Higher-level playback API4909D0 converts its caller's unsigned fourth argument using the float32 constant approximately1/30 before calling789A00. Direct callers6F636B and743C7C forward arguments from their own call contexts. Other inspected789A00 callers pass zero directly or forward different float arguments; there is no demonstrated universal three-frame default.

## Native checks

`test_playback_duration_forwarding.py` passes seven original-instruction cases for frame counts0/1/3/6/30/80000000/FFFFFFFF. It executes the x87 unsigned conversion window4909ED..490A06 and the argument-forwarding windows789A0D..789A2F and788F20..788F60. Source-selection and actor calls outside these windows are excluded, not stubbed. A diagnostic fstp instruction stores the x87 result for checking.

Three input frame units produce0.10000000894069672 seconds, exactly the duration observed after the earlier activation. This arithmetic match does **not** prove that the captured Elsa activation came through4909D0 or received a frame count of3. The live probe did not record the upstream request caller/arguments.

The alternate789A40 wrapper has the same decoded forwarding pattern but its earlier selection helper was not exercised by this numeric test. Do not infer equal source-selection behavior from identical argument movement.

## Remaining live boundary

We now have the numerical path from a supplied playback duration to native fade output. What remains for the recorded source change is the identity and actual duration argument of the playback request that supplied the replacement. A targeted request/controller/setter probe can capture that without another broad motion or mesh capture. Avoid further guessing from the selected configuration row; row Transition=-1 explicitly left this duration to a later supplied value.

Viewer transitions remain unchanged until the live request timing and arguments are linked. No hardcoded0.1-second fallback has been introduced.

Evidence: `ElsaSceneResearch/ControllerState/playback-duration-forwarding-validation.json`, `playback-duration-upstream-disassembly.txt`, `playback-duration-upstream-paths.json`.
