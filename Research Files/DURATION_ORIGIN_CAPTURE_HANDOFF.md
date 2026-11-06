# Playback request to applied duration probe

Run `F:\DisneyInfinityPortalTest\OctaneLiveInspector\CheatEngine\DI3_DurationOriginLogger.lua` in CE attached to the running game. Press F8 with Elsa idle/unpaused, and wait for the completion beep. No scene reload or movement is needed. F9 saves/stops early. Automatic limits:180 seconds or160 records. Output: `OctaneLiveInspector\Captures\ce_durationorigin_*.jsonl`.

This targets the missing caller/argument from activation210508. The earlier configuration activation, negative-duration guard and numeric fade replay are already verified separately. This capture should establish which playback wrapper's caller supplied the replacement and whether the exact value reaches controller770210 and setter525CB0.

## Four read-only hardware sites

-789A00 and789A40 entry: playback owner/current controller, raw four request arguments and caller return address. Current source identity is explicitly pre-selection; it is not assumed to be the requested source. The requested identifier stays raw rather than guessed as a string/hash.
-770210 entry: post-selection source identity, raw five arguments, prior duration and matching request link. Expected request-to-controller stack delta is60 bytes in the inspected call path; actual delta is recorded when a prior request exists.
-525CBB at setter return: actual stored duration, supplied argument and caller return77038C, linked to the controller by producer alias and16-byte stack delta. This point executes after the native duration store.

The probe accepts known PC Elsa idle ClipData sources using full payloads/prefix identity and checks controller+64/factor-node producer aliases. It refuses unrelated existing debugger breakpoints. Existing research loggers are unloaded; conflicting no-minimize F8/F9 hotkeys are released while preserving that helper's patch state. Nothing is installed until F8. No game memory/code writes are made.

It stops/beeps after one linked request/controller/write with the argument exactly equal to stored duration. Missing/mismatched request links do not count as a complete chain. Other branches can yield partial records until the limit/F9. Actor/controller replacement during source selection can make a pre-selection link invalid; such a link must not be forced. Unknown source/processor layouts are ignored. Ordered frame/alias links are not a unique actor or thread-identity proof.

## Validation

`test_duration_origin_logger_mock.py` passes four signatures, initially unarmed breakpoints, known source aliases, request/controller delta60, controller/setter delta16, expected setter caller, exact post-write value, JSONL, automatic stop/cleanup/beep. A negative stack-link fixture stays active until manual F9, records the missing link, then cleans up/beeps. Mock validation is not live request-origin evidence.

Next offline check: full source hashes; same controller/producer; callback order; stack deltas; request arg4 equals controller arg5 equals setter argument/stored field; convert the captured upstream caller return address back to preferred VA and inspect that actual caller. Do not infer a three-frame input merely because the duration numerically equals3/30.
