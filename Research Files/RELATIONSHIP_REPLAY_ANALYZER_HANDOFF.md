# Direct relationship replay analyzer

`ElsaSceneResearch/analyze_relationship_pose_capture.py` is ready for the ce_relationshippose capture. No live capture with that prefix was present when this work resumed. The original relationship probe remains the next required game observation; there is no need to repeat the earlier clock/finger-source probes.

The analyzer pairs processor/entry-stack records and rejects ambiguous or orphaned pairs. It requires exact full blob SHA256 match against the four extracted Elsa relationship records, consistent node identities/counts, selector index zero, finite values and exact payload widths. Captured virtual tables must rebase to native Float (0x1B329CC) for inputs and Dilation3d (0x1B32724) for outputs. A zero-match capture cannot pass.

For accepted pairs it feeds the original native RelationshipProcessor the captured **exit input values** and **entry initial output values**, then compares all eight output components. Entry caches may be stale; the exit snapshot reflects the completed normal native call. Raw component mismatch tolerance is 2e-5 and full values/errors are retained. No thread/actor identity or final skinning parity is inferred. Nonzero selectors and unmatched hashes remain explicit unsupported boundaries.

`test_relationship_pose_analysis.py` constructs four synthetic captures with native-generated outputs, one for each extracted hand/thumb relationship. All four replay with zero component error. Additional tests reject incorrect output-node types and detect deliberately altered output translations. These are self-consistency/tooling tests, not live game evidence. Reports and synthetic captures are clearly separated under ControllerState/RelationshipReplayFixtures; summary is ControllerState/relationship-replay-analyzer-validation.json.

Run with:

```
python ElsaSceneResearch/analyze_relationship_pose_capture.py "OctaneLiveInspector/Captures/ce_relationshippose_<timestamp>.jsonl"
```

Before interpreting a failure as a decoder defect, inspect rejected pairs, blob identity, selector, node types, stamps and initial outputs. Native replay agrees by construction with itself in synthetic tests; only the real game capture tests whether the supplied offline state/data matches live evaluation.

Next user action: run DI3_RelationshipPoseLogger.lua in CE Lua Engine with Elsa loaded, press F8 for a baseline, then supply ce_relationshippose_*.jsonl. The analyzer is now prepared to distinguish differing source inputs from differing evaluator outputs. No manual pose adjustments or viewer rendering changes were made in this step.
