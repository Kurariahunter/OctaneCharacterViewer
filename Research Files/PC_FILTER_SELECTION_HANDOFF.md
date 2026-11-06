# Native filter selection and source assignments

2026-10-19

Validated original 0x774500..0x774559 resolver window, including complete native configuration getter and cache lookups, in 12 controlled cases. Stop is before smart-reference assignment. Configuration strings, owner caches and hash buckets are prebuilt; no call-result stubs are used.

The resolver obtains the controller's selected 0x40-byte configuration row through controller +0x78 -> 0x76CC50. That getter reads handle +0x24 (row owner), handle +0x28 (row index), checks against owner +0x28 (count), and returns owner +0x24 + index*0x40. Null/out-of-range rows return null. A conflicting row zero does not change selected row one.

Row +8 is the Filter name, row +0x0C the Mirror name. Filter lookup uses mapping-object +0x0C as owner, and the owner's cache at +0x0C. Mirror lookup uses a separate cache at owner +0x44. Lookup performs exact case-sensitive string comparison after its 33x ASCII hash. Missing names return null; empty names bypass lookup. Missing handle/config/mapping/owner also selects null. At the resolver tail, the selected pointers are passed unconditionally to reference setters for controller +0x28 (Filter) and +0x4C (Mirror). The native window test does not execute those reference setters. This path has no parent-filter search; it does not prove that upstream configuration-row construction has no inheritance/merging.

Source audit: PC Elsa BENT contains 88 explicit Filter occurrences, all resolved in biped.bct. Full file/layer paths are recorded in layer-filter-assignment-audit.json. The preview-related STANCE, STANCE_PASSIVE and WALKRUN entries contain no explicit Filter or Layer declarations. The referenced grl_bm_walkrun.banm contains 54 ReferencedTrack declarations and no Filter declarations anywhere in its parsed tree. Do not infer an Upperbody filter from an upbody filename.

This source audit establishes declared assignments, not runtime activation. It does not prove the absence of concurrent BENT controllers or configuration inherited/merged before this resolver. No arbitrary filter was added to the viewer, and no pose correction was introduced.

Tests: native-filter-selection-validation.json (12 native cases), layer-filter-assignment-audit.json (88 resolved occurrences, three preview entries, 54 track references). Reproduce with ../validate_pc_filter_selection.py and ../audit_pc_layer_filter_assignments.py. Disassembly is alongside the reports.

Next trace construction of the selected configuration row from BENT File/Layer declarations and identify active controller/file/layer rows for the current preview. Existing unfiltered walk/run output must not be changed on the assumption that source filter arrays alone explain the remaining hand/braid differences.
