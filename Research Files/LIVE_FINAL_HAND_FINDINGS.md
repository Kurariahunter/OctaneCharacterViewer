# Final hand Float outputs — 2026-10-20

Capture: `ce_finalhand_20261020_002459_89558703.jsonl`, SHA-256 `9e68520a0a4ba6ae29f01bc9eec4c3443ab09d4716ba650ad5921d24bc7014e1`.

The capture stopped normally at the time limit. All 42 entry/exit pairs passed the frame, processor/output alias, contribution identity, and mapping checks; none were rejected. There are three observations for each of the 14 mapped finger/thumb ports. All exits are the normal post-setter path, so this capture does not validate a live early exit.

Every observed final Float blender has one contributor from controller `0x08A0C100`, backed by source producer `0x090BCA00`. Source/output payloads are byte-identical in all 42 observations. Source, factor, and output caches are fresh after execution. Factors at controller +2C and +30 and the filter coefficient are all 1; priority is 5 and flag +39 is 0. This is an observed pass-through case, not proof of the general multi-source blend algorithm.

Both hands have bend values -46.900001525878906, spread values 0, and thumb values -14.899999618530273. All 42 final values also match the prior preview reference values byte-for-byte. That comparison is across captures, not a synchronized animation replay.

This establishes that the previously identified output producer actually supplies these final mapped hand Float blenders. No additional scalar adjustment appears at this boundary. It does not establish unique actor identity or a complete source-to-world-to-skin chain. Earlier exact relationship and world checks were separate bounded observations.

Next investigate a synchronized chain from these final Float output nodes through relationship outputs, world transforms and final skin matrices. Compare the same nodes and evaluation stamps within one bounded capture before changing the viewer. Keep native preview free of manual finger offsets. Do not broaden the Float blender implementation to priorities, multi-source normalization or retention from this single-source case alone.

Reproduce with `ElsaSceneResearch/analyze_final_hand_capture.py` and `ElsaSceneResearch/audit_final_hand_values.py`. Reports: `ControllerState/live-final-hand-analysis.json` and `ControllerState/final-hand-value-audit.json`.
