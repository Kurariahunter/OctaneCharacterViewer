# Installed PC Elsa run preview

Source tracks extracted from the same installed-PC fro_elsa.zip as the verified model. grl_bm_walkrun.banm Run Forward references grl_bm_runf, grl_bm_run_upbody_add and human_bm_runf_lean_add (BlendMethod=1). This increment combines the first two on disjoint mapped source nodes. The lean track is excluded pending blend semantics; it is not absent from the game.

Both decoded clips last 0.6000000238418579 seconds. Lower ClipData SHA256 3b6088bca88d204c7267a58f5b64387765495876970bcc6cc7807a192378dbe3; upper 00642d2529545360d8153ae1ebf4ca15c56cff4674253faea0fcdc63f3ad48dd. Lower has no unmapped ports; upper has 806,807,808,813,814,815,850,851,854. No guessed mappings.

New curve boundary flag 0x02 uses the existing structural layout. Independent polynomial decoder agrees with original native sampling at six in-range times per curve: 96 lower cases max error 1.7550858188997154e-6; 72 upper cases max 5.4942933314094944e-8. Unknown flags still rejected. Original idle regression 276 cases max 9.230572821650185e-7 and 12 rejection checks pass. This does not implement general out-of-range Python boundary handling.

Run lower-dress leaf Transform controls 644/650 carry opcode5 scale [1.371999979,1,1] at phase zero. Earlier unit-only application rejects this. New opt-in scale support is restricted to these verified Transform nodes and vector3 opcode5, preserving stored Scale.w and Unscale. RunEval materializes these leaves with the original native typed transform/point path. Other exporters retain the strict default. No original mesh, weights, inverse binds or older preview assets changed.

Bake uses FeedbackDressEval, 120 settling ticks, 60Hz dynamics and 30Hz output: four in-place cycles, 2.4 seconds, 73 poses, 62 palette bones with 31 source-driven output paths. Remaining bones inherit bind offsets. One-shot then hold, no seamless loop or gameplay root translation. Exact game layer blend/scene collision/facial/finger behavior is incomplete. Preview is a matched-gait comparison aid, not a claim of exact original-game parity.

Open Assets/DI3PCRunPreview/Generated/Elsa_PC_Run_Preview.unity in Disney Reloaded. Left front, right side. Original recording Research_20261017_195044_169119.mp4 shows running and angular dress folding, especially around 24–26 seconds; compare those frames with the side preview. Prior walk comparison was a different gait.

Canonical bake: bake_pc_run.py; reports pc-run-animation.json, pc-run-validation.json, pc-run-file-reader-validation.json, pc-upper-run-file-reader-validation.json. Unity and render logs pc-run-unity.log, pc-run-render.log. Render helper is isolated only.
