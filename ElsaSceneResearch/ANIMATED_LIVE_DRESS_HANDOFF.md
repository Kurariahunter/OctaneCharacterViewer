# Animated live skirt capture

2026-10-16. Capture octane_20261016_231004_1792206604342552700.json.60samples, complete private-memory scan,zero failed chunks. EXE and relocated address verification passed.

## Updating objects distinguished

World-space group0x1e07fd08 (hair signature),0x1e07fdd0(left-dress signature),0x1e07fe74(right-dress signature) updates during capture. LastFrame tracks shared frame within0..1frame in all60samples. Output spans: hair0.1704025,left0.1500368,right0.2614937 world units.

Identity/zero-output group0x1dcc5a8c/0x1dcc5b54/0x1dcc5bf8 remains unchanged; LastFrame stays143 while shared clock advances1279085..1280209. This differentiates actively evaluated versus inactive objects in this capture. Template versus inactive clone lifetime is still not independently traced. Exact parameter signatures associate objects with Elsa source; ownership names have not been followed through scene instances.

## Native orientation cross-check

validate_live_dress_capture.py feeds captured world endpoint difference through original inverse-vector0x4d46f0 using captured anchor Transform, then source-axis/up vectors through original Aim0x534380. Its quaternion is compared sign-invariantly to the captured cached local Orientation node.

Across60samples per side:
- Left maximum angular discrepancy0.00000241484degrees; median0.
- Right maximum angular discrepancy0.0233285degrees; median0.
- Root-versus-anchor maxdistance8.54324e-6 both.
- Chain length(.37 times anchor uniform scale) maxerror left2.83072e-5,right2.11267e-5.

Capture is non-atomic and at large world coordinates, so concurrent updates andfloat32precision limit interpretation of small discrepancies. This provides strong live evidence for the bounded lower-dress inverse/Aim calculation given these inputs. It does NOT establish an exact original clip/time match, correct upstream pose, full simulation-force scheduling, or final renderer bone palette equivalence. Do not claim the complete cloth system is solved.

Cached local Orientation nodes: left0x1e074e38,right0x1e07531c. Anchor input nodes and header bytes are recorded in capture. Next: use those node headers and runtime producer references to locate UpperDress650/655 equivalents, then record their procedural inputs and identify playing controls/clip time. We now have actual animated outputs for that comparison, rather than a frozen-instance sample.

No game-memory writes, hooks, mesh changes or new Unity preview generated.

Reports: OctaneLiveInspector/animated-live-dress-validation.json;second-live-capture-summary.json. Script validate_live_dress_capture.py uses the existing original-EXE native fixtures. Recorded object addresses are process-state specific.
