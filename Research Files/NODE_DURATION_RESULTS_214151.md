# Live caller parameter to duration write — 2026-10-21

Capture: `ce_nodeduration_20261021_214151_252569109.jsonl`, SHA256 `ee8094ac3271ae34f0909df44c2eaa0858faccb718838e7b90df403d6941f46d`.

One complete selection/request/controller/store chain passes both native replays. The capture stopped on transition_complete after 14 raw hits and three written event records, with breakpoints released. Full source payload hashes identify passive before selection and specific03 afterward.

| Observation | Value |
| --- | --- |
| Caller return, preferred address | 1448CDB |
| Requested identifier | 8DB1FC45 |
| Live parameter block | 08F72310 |
| Cached duration parameter / block +14 | 3.0, exact bytes agree |
| Optional override +8 | -1.0; inactive |
| Runtime flags | 0; force-zero bit clear |
| Native selected seconds | 0.10000000894069672 |
| Controller prior duration | -0.03333333507180214 |
| Request, controller argument and stored duration | 0.10000000894069672, exact bytes agree |

The original 1448B61..1448C15 selection instructions choose the configured 3 units, without override or force-zero, then multiply by the executable's float32 1/30 constant. The request identifier also agrees with the parameter block's first uint32. The original controller fallback instructions replace the prior negative duration with that supplied value. Both replay results match this capture exactly.

This supplies the previously missing upstream branch evidence for a specific03 transition. It is consistent with the older specific03 producer's 0.1-second duration but is a distinct event, not a retroactive link to that event. The earlier specific01 zero-duration capture remains a different observation; its pre-selection branch was not recorded. Three units are not established as a universal default.

`test_node_duration_analysis.py` passes the live chain and rejects four changed inputs: flags, parameter bytes, identifier and stack. The 32 synthetic native selection cases and logger mock remain separate tests.

A bounded search of 139 extracted assets (910120 bytes; oct/bent/banm/animtreeoverrides/mtb) found no exact match for the captured 80-byte parameter block or its first24 bytes. This does not rule out serialized or transformed data. The live address is not a file offset, and no file schema mapping is claimed.

Next work: trace the parameter-view construction/loader and identify how its identifier and +14 parameter are populated from serialized node data. Keep the observed selection adapter separate from automatic viewer scheduling until that input mapping is established. No additional user capture is requested for this result. No viewer pose correction or finger fix is introduced.

Reports: `ElsaSceneResearch/ControllerState/node-duration-analysis-214151.json` and `node-duration-file-search-214151.json`.
