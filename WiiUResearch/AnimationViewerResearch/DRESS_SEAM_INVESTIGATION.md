# Wii U Elsa dress fold investigation — 2026-10-24

Recording: Research_20261024_222051_730555.mp4. The visible lower dress fold changes during the specific idle. This is not established as intended game behavior.

## Measured evidence

The actual source mesh, weights and all 153 cached palettes were tested without editing any of them. The earlier whole-body test found 522 coincident vertex pairs with zero separation. The focused test includes 408 body triangles influenced by the four dress bones, 669 nonzero-length edges and 44 coincident vertex pairs; those pairs also remain exactly together throughout playback.

The current full palette stretches its worst dress-region edge to 2.02127 times bind length at clip time 0.466667 s. Vertices 4660 and 4665 connect an approximately 90% right-dress influence to an approximately 50/50 right/left dress influence near mesh X=0. This identifies differential left/right dress deformation as a concrete area to investigate; it does not prove that this edge is the visually reported rear fold.

The earlier 57-output cache, with bind-relative dress fallbacks, is worse by this metric: maximum edge ratio 5.94586 at 4.8 s, across a dress/knee/ankle transition. Therefore reverting the dynamic dress outputs is not an evidence-based fix. The chain implementation improves this metric but does not eliminate distortion.

## Limits and next boundary

Edge stretching is not a triangle self-intersection test. Zero split separation excludes torn coincident mesh splits, not folds or overlapping panels. Neither test establishes Wii U game parity. Collision remains absent, but these measurements alone cannot identify missing collision as the cause. Source chain anchors, retained orientation feedback, activation/warmup and bind/output space must be compared against runtime evidence before changing those mechanics. Do not weld vertices, tune bone angles or claim the seam is fixed based on these checks.

Reproduce with audit_dress_deformation.py, then with argument wiiu-source-mesh-animation.json for the fallback comparison. Reports: dress-deformation-audit.json and dress-deformation-audit-fallback.json. The viewer and baked animations were unchanged.
