# Local finger to world and matrix continuity probe

Run `DI3_WorldChainLogger.lua`, return to gameplay, F8 and move Elsa until the beep. Send `ce_worldchain_*.jsonl`. F9 stops early. The probe uses four read-only hardware breakpoints, with no injected code or game-data writes.

Sites: relationship exit 54CA19, world Transform exit 57CC15, world Dilation exit 4D798E, and Dilation-to-packed-matrix exit 4DEEBE. Unlike the older world probe, every eligible relationship execution refreshes its full blob and local output snapshots. Subsequent stages carry the exact predecessor event sequence. The analyzer requires unchanged node/producer identity, payload bytes, and evaluation stamps, as well as typed fresh snapshots and native operation replay.

This targets the index/middle chains of both hands, including second-joint matrices. It does not trace thumbs, renderer palette consumption or complete mesh deformation. Relationship candidates require offline full blob hash identification. Stop at 256 records or ten seconds; an event budget can end between downstream stages. Missing stages must be reported rather than inferred.

Validation: four Lua 5.3 mock cases passed: linked downstream graph with repeated relationship refresh and packed offset 0x40; invalid source link; invalid signature; partial breakpoint cleanup. Completion beep is checked only after successful F9 save and cleanup, silent unload/setup failures. Live byte/stamp continuity remains to be tested.

Analyze with `analyze_finger_world_capture.py CAPTURE ControllerState/live-world-chain-analysis.json`. The new schema activates strict continuity; older capture schemas retain their prior bounded validation behavior. Do not substitute manual finger corrections in the viewer.
