# Preview boundary audit

Audited all four hash-pinned OCT profiles and selected Elsa BENT entries (STANCE, STANCE_PASSIVE, WALKRUN). Clip ranges are declared:

| Profile | MinTime | MaxTime |
|---|---|---|
| elsa_bm_idle_active | 0 | 4.199999809265137 |
| elsa_bm_idle_passive | 0 | 6.166666507720947 |
| grl_bm_walkf | 0 | 0.800000011920929 |
| grl_bm_runf | 0 | 0.6000000238418579 |

No declarations with loop/cycle/boundary/wrap/repeat in their names occur in these OCT records or selected BENT entries. This is a name-based audit, not proof flags cannot be encoded elsewhere. WALKRUN refers to a BANM; its upstream controller setup remains relevant.

The latest live publication capture contains boundary bytes 0xF8 and 0xAE, with state byte +0x63 values including 0 and 3. Captured ranges do not establish identity with these four preview clips. Do not infer a profile match from duration or assume the tested 0x0E byte is universal. The low nibble of 0xAE matches the tested cyclic selector, but high flag bits remain outside that adapter.

Static constructor evidence: two sites installing AnimCurveControlProcessor vtable 0x1B35334 initialize the word at +0x62 to **0x0358**, at preferred 0x54A03D and 0x7732BD. Thus default boundary byte is 0x58 and adjacent state byte is 3; it is not the cyclic fixture byte 0x0E. These constructors initialize rate fields +0x44/+0x48 to 1 and lower/upper range defaults to 0/1 before later setup. This is instruction-level evidence, not a new full-constructor execution test.

This audit prevents silently enabling an unsupported timing configuration in rendering. Existing bake and separately validated cyclic adapter remain available unchanged. Next trace mutations/setup of +0x62/+0x63 from these constructor sites through controller configuration, establish which applies to each selected preview, and extend the time adapter to that verified mode before wiring rendering.

Reproduce with ElsaSceneResearch/audit_preview_time_boundaries.py. Report: ControllerState/preview-time-boundary-audit.json. Constructor disassembly: ControllerState/curve_time_constructor_defaults.txt. No new capture is needed yet.
