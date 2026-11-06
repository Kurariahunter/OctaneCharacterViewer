# Three PC Elsa specific idles — full palette checkpoint

Update: FULL_PALETTE_LOCOMOTION_HANDOFF.md records separate tested62-bone forward-walk and forward-run artifacts. The idle artifacts below are preserved.

2026-10-22. All three distinct source clips now have bounded native previews with62/62 palette bones evaluated from source graph paths and zero bind-offset palette fallbacks.

In the viewer choose **Open evaluated animation**, then one of:

| State | File in NativePreviews | Duration | Saved samples |
| --- | --- | ---: | ---: |
| IdleA / specific01 | native-idleA-full-palette.json | 5.066666603088379s | 153 |
| IdleB / specific02 | native-idleB-full-palette.json | 6.666666507720947s | 201 |
| IdleC / specific03 | native-idleC-full-palette.json | 5.0333333015441895s | 152 |

All paths above are relative to `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/`.

The source files are hash-verified PC assets. Each preview enables the eight facial outputs, four eyelids, two eye-direction outputs and two forearm overlays alongside the previous body/dress/hair/finger graph. Each uses its own full XML IdleA/B/C state path with the existing explicit native Float/Dilation/Transform fade fixture. No new empirical pose adjustment or automatic event scheduler was added.

## Checks

All three bakes pass the existing endpoint, native matrix, shear and dress invariants. The audit checks distinct source hashes, identical62-bone coverage, no fallback parents, correct explicit state path, enabled source-path options, finite matrices, strictly increasing sample times, and final duration. It records per-bone matrix-component changes from the first sample as motion diagnostics, not visual error scores.

Maximum endpoint error across the three bakes:8.959200081264404e-6. Maximum native matrix component error:2.980232238769531e-7. Maximum TRS shear:1.7347701396478782e-7. Dress root error is zero. Maximum dress segment-length error:3.9950628044627123e-7.

Run `audit_full_palette_idles.py` to reproduce the coverage audit. Results: `NativePreviews/full-palette-idles-audit.json`; per-bake results are the adjacent `.validation.json` files.

Bake A/B using the FOREARM_OVERLAY_HANDOFF.md command with source suffix01/02, matching output letter and explicit IdleA/IdleB state path. All flags remain opt-in and viewer startup behavior is unchanged.

## Evidence boundary and next step

The user approved the preceding eye/lid preview. New forearm overlays and the full-palette A/B artifacts still need visual confirmation.62/62 coverage does not establish native game parity, correct missing-channel defaults, automatic branch/event timing, collision context, or every animation/character.

Next: compare all three idles visually, then broaden the supported native graph to locomotion with the same complete palette and explicit source composition. Keep the known running-index-finger issue separate from successful idle coverage; do not add empirical corrections to the native baseline.
