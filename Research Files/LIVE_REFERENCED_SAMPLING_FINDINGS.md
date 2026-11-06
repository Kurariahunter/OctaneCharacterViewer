# Live referenced sampling validation — 2026-10-19 22:32

Capture ce_reftime_20261019_223229_82808250.jsonl:48 referenced-sample observations and48 group child-buffer observations,96eventlimit.42buffers have112rows;other six42/45rows are explicitly outside selected biped mapping. Sources identified via same track/asset/blob prefix candidates. Latest observed sampling record joined by track/source and preceding sequence; not proof of thread/call-stack identity.

39 checked child-buffer records,1454 scalar/translation/rotation channel comparisons, exactly zero component error and zero missing masks. Includes runf,runlf,runr,run_upbody_add and forward/diagonal/right static lean. Lean uses existing bounded read_static rather than animated Clip reader. This is positive file-sampling-to-runtime-child-buffer evidence at recorded local times. All14upperbodyhand scalars are included where present, not merely world transforms.

Nine boundaries remain: six no unique source candidates (mixed42/45row buffers), three runrf records reject unknown curve format. Unsupported records are excluded and listed, not counted as passes. Source match for larger clips remains256byte prefix; lean candidate fileblocks fully covered. Runtime row mapping uses the previously file-derived112row biped LocalToPortIndices, not an independently captured row table in this probe.

Verified raw52byte row layout from59DF90: scalar at+0 withmask1; translation at+4,+8,+C masks2,4,8 (vector0xE); rotation+20 fourfloats mask0x100; scale components+10,+14,+18. Do not reinterpret raw row translation as floats0..2. The existing one-row blend helper packs logical fields for isolated arithmetic; no runtime row buffer imported into it here.

Analyzer analyze_referenced_time_capture.py writes checked_subset_matches plus explicit boundaries. Negative fixture changed one captured scalar by1 and correctly fails subset matching. No viewer composition/pose changes; no hand offsets. Next decode unknown runrf curve variant and inspect blended destination after native dispatcher, keeping child sample validation distinct from parentweight/phase scheduling and finalpalette parity.

Reports ControllerState/live-referenced-time-analysis-223229.json and.prefixes.json, referenced-time-analyzer-validation.json. Completion beep remains in capture scripts.

## Right-forward boundary flag resolved — 2026-10-19
Source grl_bm_runrf.oct SHA25642c58f54a1002020811d25e8db2982a5aa1c6a0d44ca02fda63d5e229ddb73da contains one curve headerkind0x0410:dimension1,boundaryflags0x10,curveindex4,offset3424. Reader previously admitted only0/2/0x12. Native522CF0 extracts dimensions independently at522D08 and low before-range bits withAND7 at522DD7; after-range bits withAND38 at522F68.0x10 shares the same validated interior layout. Added exactly0x10 to allowlist, not blanket acceptance of other flags.

validate_curve_flag10.py:31 native in-range samples compare exactly against established0x12 mode on identical curve coefficients. Native before/after-range observations recorded separately; modes are NOT claimed equivalent outside range. Two unverifiedflags8/0x3FF still reject. Full runrf source structural parsing passes.

Reanalysis of live22:32 referenced-time capture now checks42records/1598scalar,translation,rotationchannels,zero error/zero missing masks. The three previously unsupported runrf records each contribute48exactchannels. Six no-unique-source mixed42/45row records remain explicit boundaries; no false universalpass. Earlier39records remain exact. No additional game capture needed for this step, no viewer pose offsets or composition changes.

Reports ControllerState/curve-flag10-validation.json,curve-flag10-native-boundaries.txt and updated live-referenced-time-analysis-223229.json. Next stage is capture/compare destination buffer after5A14D0, preserving source versus destination distinction and exact sample-time evidence.
