# Native node duration capture

The previous live capture (ce_durationorigin_20261021_212000_251258593.jsonl) linked a zero-second playback request to the controller and actual duration write. It did not observe how the caller selected zero.

Run `F:/DisneyInfinityPortalTest/OctaneLiveInspector/CheatEngine/DI3_NodeDurationLogger.lua` in Cheat Engine attached to the same PC game. Leave Elsa idle, unpaused, with no menu open. Press F8 once. No movement or scene reload is required. F9 saves early. Automatic completion or the 180-second/160-record limit saves, releases this probe's breakpoints, then emits a best-effort beep. Unrelated breakpoints are refused, not removed.

Send the new `ce_nodeduration_*.jsonl` from `F:/DisneyInfinityPortalTest/OctaneLiveInspector/Captures`.

The four read-only execution observations are preferred addresses 1448B61 (before duration selection), 789A40 (request), 770210 (controller), and 525CBB (after duration store). The first signature checks its relocated absolute operand against the current module base. Caller ESI, ownership pointers and stack relationships link the pre-selection observation to the later request. It records the cached parameter, parameter block, optional override and runtime force-zero flag. A complete linked write can stop the capture; analysis separately checks original native selection math against the request and original native fallback math against the stored duration.

Validation: mocked complete chain and mismatched-stack rejection pass, including F9/automatic cleanup and beep. Thirty-two synthetic cases execute the original getter and selection instructions successfully. These are not live validation of the new probe. The native adapter covers finite parameters and the observed instruction window, not the full caller or scheduler. A live parameter pointer does not establish its source-file offset. No finger-pose or viewer change is claimed by this probe.

Analyzer: `F:/DisneyInfinityPortalTest/ElsaSceneResearch/analyze_node_duration_capture.py`, with positional capture path and required `--output` JSON path.
