# Index-to-middle gap diagnostic

User clarification/screenshot 114221 identifies the gap between index and middle fingers as the intended adjustment. A new Close index / middle gap slider rotates the index base toward the corresponding middle bone's longitudinal direction, using a shortest-arc direction rotation. This avoids guessing mirrored local axes. The index tip follows the base delta rigidly, preserving spacing. Default zero preserves decoded pose; one aligns the two base directions, which does not guarantee surface contact or anatomically correct skinning. Other fingers stay unchanged.

Before testing: Restore fingers (tip 100 percent, bend offset zero, gap zero). The screenshot showed tip at zero, which independently straightens the index tip. Adjust only the gap slider next. This is a runtime visual diagnostic, not a confirmed file-decoder correction or saved source-pose modification.
