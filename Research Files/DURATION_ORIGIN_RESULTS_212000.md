# Live playback duration origin — 2026-10-21

Capture `ce_durationorigin_20261021_212000_251258593.jsonl`:134,900 bytes, SHA256 `533c4559536bb446f0ce493fdfa137efe616fabc6f57787906ad6d7f3df598c5`. One request, controller call and completed duration write; normal transition_complete stop; all breakpoints released. Only9 raw hook hits were needed.

## Observed linked chain

The request snapshot shows current source `elsa_bm_idle_passive`. After source selection the same controller/producer resolves to `elsa_bm_idle_specific01`; full PC ClipData hashes verify both identities. Raw requested identifier is8DB1FC43; no hash algorithm/name mapping is inferred from that value.

Request wrapper789A40's caller return is preferred1448CDB, immediately after the call at1448CD6. Request argument4 is **0.0 seconds**. The matching controller770210 receives exactly0.0 as argument5, with verified60-byte request/controller stack progression. The controller's prior duration is-0.03333333507180214. Setter525CB0, observed after its write at525CBB with return77038C, receives/stores exactly0.0. Identity, callback order, argument forwarding and stored header value all agree. The native negative-duration fallback reproduces that replacement.

This closes the request-to-write chain for this specific passive-to-specific01 event. It disproves a universal0.1-second replacement assumption. It does not explain every source change or retroactively assign this caller/value to the earlier specific03 capture.

## Actual caller's parameter-selection path

Instruction decoding from routine1448AE0 reaches the captured call1448CD6. Getter1441CD0 reads a float at parameterBlock+14 through a view's data pointer; the result is stored as a local duration parameter. An optional object at caller+2C can replace it using its+8 float when nonnegative. A runtime flag at caller+114, bit04, forces this parameter to zero and clears that bit. Negative selected values are clamped to zero, then multiplied by float32(1/30) before forwarding.

These are caller parameter/override fields, separate from the configuration row's Transition integer at row+24. Do not conflate their types or ownership. The capture did not record this caller object's original parameter/override/flag values, so it does not show which branch selected zero.

`test_animation_node_duration_selection.py` executes the original getter and selection/conversion windows in32 cases. Configured values, missing/negative/nonnegative overrides, force-zero flag clearing and negative clamping all pass. The whole caller's actor lookup/selection/callback flow is excluded, not stubbed.

## Validation and next boundary

`analyze_duration_origin_capture.py` reports one verified chain and no rejected boundaries. `test_duration_origin_analysis.py` confirms the live chain and rejects changed forwarded arguments or stored values. Machine report: `ElsaSceneResearch/ControllerState/duration-origin-analysis-212000.json`. Caller tests/disassembly: `animation-node-duration-selection-validation.json` and `actual-playback-caller-duration-disassembly.txt` in that directory.

Next connect the identified caller's parameter block/override/force-zero state to the file-backed node data and runtime activation. The numerical request/negative-default/fade path is established for supplied values; automatic source scheduling and the parameter choice are still separate work. No generic motion capture is needed for this result. The viewer has not received guessed duration constants or pose adjustments.
