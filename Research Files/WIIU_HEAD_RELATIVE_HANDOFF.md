# Head-relative eyelid diagnostic — 2026-10-24

The standalone mesh diagnostic now offers Head-relative diagnostic (default) and Absolute world fixture modes. A Focus eyelids button centers the affected region and increases zoom. Reset restores whole-model framing.

The head-relative mode is an inspection-space transform, not a decoder correction or new game behavior. For column matrices:

    rebasedSkin = headBindWorld @ inverse(animatedHeadWorld) @ eyelidWorld @ inverseEyelidBind

This removes the sampled Head transform and places the local eyelid output in the head bind frame. Coordinate reflection is applied consistently before deforming the exported reflected mesh. Assertions verify that headBindWorld @ inverse(animatedHeadWorld) @ animatedHeadWorld returns headBindWorld, all outputs are finite, and all 5,184 vertices without eyelid weights remain exactly unchanged in both modes.

Maximum relative vertex displacement at start/mid/end is approximately 0.00000207, 0.00765172 and 0.00000207 source mesh units. The near-bind endpoints and moving midpoint are useful diagnostics; they do not independently prove a game-perfect blink. No angle offsets, smoothing or hand tuning were introduced.

JavaScript syntax check passes. Automated browser visual inspection was unavailable because its URL policy rejects local file URLs; no workaround was attempted. Open eyelid-preview.html locally to inspect the two modes. Production viewer unchanged; still four eyelid influences and three snapshots, not a complete actor palette or native playback.
