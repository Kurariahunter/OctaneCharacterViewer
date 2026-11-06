# Original-game reference recording, 2026-10-16

Source: C:/Users/Kurar/Videos/DI Research/Research_20261016_194811_253384.mp4
H.264,2560x1440,127.833333seconds. FFprobe readable; FFmpeg frame extraction succeeded. Adjacent log contains only the gdigrab startup warning about insufficient frames to estimate rate; this alone is not a recording failure.

Reviewed a five-second-spaced overview and original-resolution crops at2seconds(front, head partially obscured by overlay) and60seconds(rear). In these visible idle poses the skirt hangs relatively narrowly and no comparable broad persistent side bulge is apparent. Some idle-break gestures (hand on hip) occur, so the precise source clip and phase are NOT established. Camera perspective, pose and image scale differ from the Unity diagnostic. Visual evidence supports investigating the conversion but cannot identify an erroneous bone/channel or prove an exact active-idle mismatch.

Artifacts: game-reference-contact.png; game-reference-front.png; game-reference-rear.png. game-reference-front-start.png at0seconds is obstructed by an overlay and unsuitable as a pose reference. Original recording ends with desktop UI; no instruction visible there was treated as a user request.

Next useful comparison: match an unobstructed frame's body/foot pose to the corresponding source clip/time before comparing the skirt silhouette or runtime transforms. No mesh or importer edits made from this recording.

## Follow-up: pose selection

Reviewed front crops at2-second intervals from4through28seconds, then0.5-second intervals from13through19.5seconds. The footage alternates a repeated hand-on-hip stance with two-hand gestures; arms-down moments near14/18seconds in the coarse sheet belong to gestures/transitions and must not be labeled sustained active idle. No exact active/passive source clip or phase is confirmed from these images.

Selected11seconds as an unobstructed front hand-on-hip reference within the comparatively steady8-13second interval. Saved game-reference-steady-11s.png at original pixel scale, plus game-idle-front-detail.png and game-idle-transition-detail.png. This is a candidate visual reference, not a matched active-idle frame. Our Unity diagnostic holds arms at bind, so arm silhouette cannot be used to validate an exact clip match in that preview. Body/feet perspective alone is insufficient for reliable frame matching here. A runtime clip/state identifier or additional source-driven arm evaluation would provide a stronger match. Keep the existing native channel/default-loader investigation as the next executable work; do not tune the skirt against an assumed active pose.
