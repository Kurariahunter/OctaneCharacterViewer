# Live finger inputs — 2026-10-19

Capture ce_fingerinputs_20261019_205652_77071921.jsonl stops normally at 120 blend events; 12 boundary events are rejected by the original blend-return checks. It contains eleven mapping snapshots. Analysis artifacts: ElsaSceneResearch/ControllerState/live-finger-input-analysis.json and analyze_finger_input_capture.py.

257 existing packed mapping checks pass, plus 628 targeted typed port/inverse mapping checks. Those targeted observations comprise 244 stamp-matching cached values and 384 stale values across 24 controller/port groups. 400 other per-port records explicitly report absent/mismatched ports; these are not decoded as values or index-zero fallbacks. Every decoded payload has captured Float RTTI and exactly four bytes interpreted.

## Strongest fresh source pattern

Controller 0x08A0C100 yields 58 fresh observations per port, all constant:

| Port | Value | Active-idle file phase-zero value |
|---|---|---|
| 483 left Index1 | 1.399999976158142 | exact match |
| 510 right Index1 | 1.399999976158142 | exact match |
| 805 left Thumb2 | -7.400000095367432 | exact match |
| 812 right Thumb2 | -12.59999942779541 | exact match |

The captured state range is 0..4.199999809265137, also matching the active-idle profile. Its first observed factor2C/factor30 values are 1/1 with no filter object. These combined facts support an active-idle source-pattern match; they are not a unique actor identification or a final blended-scalar output capture.

Another source (0x08B0B200) contributes three fresh observations per port, all zero. Other biped sources are stale in this probe: e.g. -28.1 index values at 0x07F8B600 have mismatched stamps and a first observed factor2C of zero. HeadTurn has zero candidate coefficients for these ports and stale values. Do not use stale cache contents to overwrite the preview or infer a missing correction.

## Implication

The four fresh values match extracted active-idle scalar decoding. This capture does not validate the run upper-body source pattern (-46.9 bends/-14.9 thumbs) and cannot justify replacing it with idle values. It may have sampled another active source or actor alongside intended movement. Keep that distinction explicit rather than claiming the run decoder is wrong or that the user failed to move.

Relationship evaluation and selected hierarchy math are already independently compared with original code, but their exact live inputs/output transforms and final blend remain unjoined. A visual finger mismatch can still originate in final layer composition, relationship setup/initial fields, unchecked downstream operators or skinning interpretation. No pose values, offsets or composition were changed based on this capture.

Next: trace the identified source/controller context to final finger control/relationship output nodes, or target run-source lineage before interpreting another source snapshot as run data. Preserve the valid idle scalar match as evidence and avoid another broad undirected gameplay recording.
