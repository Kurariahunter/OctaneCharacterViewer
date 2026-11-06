# PC run lean layer: static controls decoded, blend integration pending

2026-10-17. Existing Unity run preview and original mesh remain unchanged.

## Confirmed asset findings

human_bm_runf_lean_add.oct is a static ClipDataBlock, with no timed curves. It contains four packed command records. All four ports resolve through the verified PC model mapping:

| Port | Node | Control | Rotation magnitude | Overlap |
| --- | --- | --- | --- | --- |
| 92 | 240 | Cntrl_Body_2 | about 11 degrees | lower run |
| 545 | 267 | Cntrl_Head | about 13.798 degrees | upper run |
| 754 | 352 | Cntrl_Shoulder_Spin_Left | about 6.480 degrees | upper run |
| 755 | 370 | Cntrl_Shoulder_Spin_Right | about 6.480 degrees | upper run |

The body also has zero translation. Angles above are quaternion magnitudes, not claims about Unity signed Euler angles. Full original xyzw values are in pc-run-lean-static-validation.json. Static offsets can still produce time-varying final output when blended with the animated base graph.

Unlike combining the disjoint lower and upper run channels, applying this layer directly would overwrite existing animated controls. That is not a valid additive implementation.

inspect_pc_run_lean.py validates the specific zero-duration/no-curve PC header, empty timed table, float pool and existing packed static descriptor layout, checks normalized quaternions and mappings, and rejects four malformed inputs. It is a bounded static reader, not a generic duration-zero Clip extension. It does not change the animated Clip reader.

## Executable trace

BlendMethod string is at preferred-image VA 0x1b4c2dc; reference is push at 0x78079e (immediate operand 0x78079f). Loader calls the property lookup, reads the numeric property, and writes a boolean nonzero result to destination object+8 at 0x7807df. This corroborates a mode distinction, not a complete semantics/name assignment.

The previously discovered runtime blend execution at 0x4e35d0 reads contribution records, controller+0x39 flag, weights and priority/group fields. Its branch treats flagged contributions separately from the ordinary weight sum; subsequent accumulation calls helpers including 0x4bb4a0. The disassembly reads extended scale-bearing payload fields; the old diagnostic name DilationBlend_4e35d0 must not be treated as independent proof of its exact supported payload type.

Missing proof: how the loaded track mode at object+8 reaches runtime contributor flag+0x39 for this track, which blend executor receives each control type, and native composition/order/reference-pose semantics. A boolean source property and a boolean runtime flag are not enough to connect those facts.

Next executable work should trace the track-to-controller construction/update that transfers mode, identify the control-type blend dispatch, then construct a bounded native accumulator replay with noncommuting rotations and weighted/identity controls. A matched live run contributor capture can independently verify the link and result. No guessed quaternion multiplication, base-pose subtraction, or visual-only lean fix has been exported.

## Files

- inspect_pc_run_lean.py
- pc-run-lean-static-validation.json
- pc-run-lean-tuples.json
- pc-run-lean-static-channels.json (initial raw decode)
- run-lean-blendmethod-loader-disassembly.txt
- dilation-blend-4e35d0-disassembly.txt (initial bounded window; not entire function)

Canonical folder F:/DisneyInfinityPortalTest/ElsaSceneResearch. Mirrored in Disney Reloaded/Tools/ExecutableResearch/DressResearch.
