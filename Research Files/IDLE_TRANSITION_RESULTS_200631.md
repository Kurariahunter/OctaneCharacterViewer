# Live idle transition result — 2026-10-21 20:06:31

Capture: `ce_idletransition_20261021_200631_246849171.jsonl`, 5,578,733 bytes, SHA256 `7b69e822c9d45e41b8a7d02360645f85ed018384219b5cc9cc065cb895d12a68`.

113 pose records; normal `transition_complete` stop; all breakpoints reported released. 109 rows accepted by ordered source/controller/port/stamp/output checks. Four rows were rejected because their clip prefix was unknown; they provide no parity evidence.

All 109 accepted rows (654 finger scalar observations) match original-PC file sampling exactly at the recorded sampler time. Sources cover passive, active, active-to-passive, and all three specific idles. Actual sample time and later observed clock agree in every accepted row. This capture does not establish that they always agree in other executions.

105 accepted rows also have identical source and final scalar values. Four differ: sequence33 left active, sequence34 right active, sequence95 right specific02 at time0, sequence97 right specific02 at time0.0703125. Their factor30 values are approximately0.11718749,0.41015622,0.19531249,0.89843744 respectively. Other accepted factors: factor2c=1, filter coefficient=1, priority=5, flag39=0.

Largest source-to-final difference is0.04682159423828125 on port516, sequence97: source -20.72901725769043, final -20.77583885192871. Source sampling is exact there. The difference is visible at the scalar blender return, before the relationship reads its inputs. This localizes these new observations to the scalar blending stage rather than a file-curve decode discrepancy.

This is not proof of the precise fade formula, previous-pose source, or thread/call-stack identity. It also does not retroactively prove the cause of sequence55 in the earlier092605 capture. Do not add empirical timing offsets, multiply source values by factor30 alone, or treat a fitted blend as native evidence.

Next: inspect/replay the native scalar blender with its prior output and captured factors, including both return paths, to establish the transition rule. Extend the narrowly scoped probe only if the native routine requires an input not yet captured. Keep viewer poses unchanged until that replay is validated. No additional generic capture is needed yet.

Machine report: `ElsaSceneResearch/ControllerState/idle-transition-analysis-200631.json`. Generated with `analyze_idle_transition_capture.py`.
