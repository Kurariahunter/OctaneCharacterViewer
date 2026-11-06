# Elsa-only index capture

User loaded a Toy Box containing only Elsa, with both mounts removed. This is scene isolation supplied by the user, not independent renderer identity proof.

Run `DI3_IsolatedIndexLogger.lua` inside Cheat Engine attached to DisneyInfinity3.exe. Return focus to gameplay; F8 starts capture. Stand idle for approximately two seconds, run and change direction for approximately six seconds, then release movement until the completion beep. F9 saves early. Send `ce_isolatedindex_*.jsonl`.

Four read-only hardware execution sites: final Float setter return 4E35C0, hand relationship return 54CA19, first-joint world Transform return 57CC15, second-joint matrix return 4DEEBE. No game writes or forced evaluation. Hand relationships are sampled at most once per processor per 500 ms, with downstream records limited per seed/slot; capture ends after 12 seconds or 512 written events.

Final scalar observations retain source contribution controller, reverse-checked port mapping, source node and candidate map-owner name. Relevant observations are embedded in hand relationship records. The matrix record captures its world Dilation input plus that producer's local input and converter, allowing native replay without a fifth breakpoint. Full relationship hashes and typed freshness/byte continuity must be checked offline. Raw scalar callbacks do not increment written-event count.

The owner name is only a candidate from a previously researched layout. This capture does not guarantee a rendered-actor identity. Use scene isolation, mapped owner/controller grouping and observed idle/run changes to assess ambiguity explicitly. Do not label a shared rig/class name as Elsa actor proof.

Mock checks pass for scalar port483/controller links embedded in relationship snapshots, linked world/matrix graph, half-second seed throttling, invalid source rejection, signature failure, partial install cleanup and completion beep. Live owner-name readability and actual actor association remain pending.
