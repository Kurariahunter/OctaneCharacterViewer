# Same-capture hand scalar to relationship probe

Run `DI3_HandChainLogger.lua`, return focus to gameplay, press F8 and move Elsa until the completion beep. Send `ce_handchain_*.jsonl`. F9 stops early. Three read-only hardware breakpoints; no injected code, game-data writes or forced evaluation.

The scalar post-setter site 4E35C0 observes output node, producer, four payload bytes, and cache stamps. At relationship entry 54C9A0 and exit 54CA19, candidate hand/thumb snapshots include the latest scalar observation joined by exact input-node address. Offline checks require unchanged bytes and stamps, fresh caches, full relationship blob hash matching and native relationship replay. An earlier setter observation alone does not prove nested evaluation or player actor identity.

Budget: 192 relationship records or ten seconds. Raw scalar observations are kept in memory and included only when linked to a captured relationship. Cap or stop may leave an incomplete relationship pair, which must be rejected offline. This capture stops at relationship output, not world or skin matrices.

Validation: Lua 5.3 compilation and three lifecycle mock cases passed (normal F9 save/cleanup/beep, bad signature, partial breakpoint-install cleanup). Live data joins are not validated yet. Run `analyze_hand_chain_capture.py` for exact-node/freshness links and `analyze_relationship_pose_capture.py` for hash-checked native replay. Keep outputs separate from earlier capture reports.
