# Source track mode dispatch and run lean comparison

2026-10-17. Separate preview; original model and earlier animations preserved.

## Delivered scene

C:/Users/Kurar/Disney Reloaded/Assets/DI3PCRunLeanPreview/Generated/Elsa_PC_RunLean_Preview.unity

Both models face sideways. Left is the preceding run without lean; right adds human_bm_runf_lean_add through the original direct clip-buffer additive path at authored forward-run weight1. Four in-place0.6second cycles,2.4seconds total; then holds. It is an experimental source-track reconstruction, not full live actor/layer parity. Nine unmapped upper-run ports remain excluded. Original mesh, weights, inverse binds and materials are retained. Visible angular dress folds are not claimed fixed.

## New executable path

The source-track constructor0x5a2260 initializes mode+8 to0. Referenced-track constructor0x5a23f0 calls it and installs vtable0x1b38ec4. The common property loader0x780770 writes the normalized BlendMethod value at the same+8 field. The base track copy method0x5a25f0 copies source+8 to destination+8 at0x5a261a..0x5a2620; referenced-track copy0x5a27c0 invokes that method before copying its additional fields.

A group child evaluator0x5a1590 evaluates a child through virtual slot+0x24, then tests child+8 at0x5a15f4. The boolean passed to0x5a14d0 is (child mode==0). Other traced child paths0x5a16cf/0x5a1724/0x5a1faa perform a related mode test. This provides a direct source-track dispatch path; it does NOT prove a transfer to the separate runtime contributor byte+0x39 discussed in earlier notes.

Dispatcher0x5a14d0 selects:

| Child mode | No channel map | With channel map |
| --- | --- | --- |
| zero |0x59f3e0 |0x59f6a0 |
| nonzero |0x5a00d0 |0x5a0490 |

The tested unmasked zero-mode routine interpolates authored components. The tested nonzero-mode routine adds weighted translation, multiplies scale by the weighted source scale delta and composes rotation before normalized interpolation. No word such as additive is assigned merely from the flag; numerical tests corroborate it.

## Native checks

validate_pc_source_mode_dispatch.py executes three original instruction windows in sequence with synthetic objects:

1. Accepted raw value normalization at0x7807d4..0x7807e2.
2. Original mode field copy at0x5a261a..0x5a2620.
3. Group mode test/call at0x5a15f4..0x5a1616, which executes real dispatcher0x5a14d0 and the complete selected unmasked helper.

Sixteen cases use raw mode0,1,2,-1 and weights0,.25,.5,1. Each checks the visited helper and consumed buffer depth. With noncommuting mixed-axis rotors, nonzero translation and nonuniform scale, the tested formulas are:

```text
mode0:
  t = base_t + w*(source_t-base_t)
  s = base_s + w*(source_s-base_s)
  q = normalize((1-w)*base_q + w*source_q)
nonzero mode:
  t = base_t + w*source_t
  s = base_s * (1 + w*(source_s-1))
  composed_q = HamiltonMultiply(source_q, base_q)
  q = normalize((1-w)*base_q + w*composed_q)
```

These formulas use controlled positive-dot rotations; general hemisphere behavior is handled by original native code, not claimed from this small formula comparison. Quaternion conventions remain source xyzw, before the established coordinate reflection.

Max rotor error7.576069027681598e-8; translation/scale error each9.536743172944284e-8. Initial base*source candidate was rejected (error~0.24208), then source*base passed. This is a discriminating order test.

native_pc_clip_buffer_blend.py exposes a bounded one-row adapter through the same original dispatcher. Eight adapter-vs-group-window cases match exactly, and a rotation-only source mask preserves unrelated translation/nonuniform scale. Float source Dilation scale defaults are expanded for the buffer fixture; lean export modifies only authored translation/rotation fields and preserves existing scale fields.

## Bake and scope

bake_pc_run_lean.py preserves the preceding FeedbackDressEval run path and its lower-dress nonuniform scale support. It applies lower/upper run channels, then the four verified lean control records in source group order through native buffer masks. Native IK, persistent dress, packed skin-matrix conversion and palette export follow.

All numerical bake invariants pass. Isolated Unity build validates TRS reconstruction, finite skinning and fresh saved Animator motion. Six rendered poses passed visual inspection; saved comparison scene uses original materials. The production preview depends on the existing DI3PCRunPreview base-run prefab for its left instance. It contains its own lean animation/controller/prefab for the right.

Remaining: full parser/parent scheduling execution, mapped-channel variants, complete actor state-machine weights and priorities, exact live ownership of the lean track, source mode-to-runtime contributor relationship, all facial/finger channels, gameplay locomotion and seamless looping. No claim that all game blending has been reconstructed.

## Files

- validate_pc_source_mode_dispatch.py; pc-source-mode-dispatch-validation.json.
- native_pc_clip_buffer_blend.py; validate_pc_clip_buffer_adapter.py; pc-clip-buffer-adapter-validation.json.
- bake_pc_run_lean.py; pc-run-lean-animation.json; pc-run-lean-validation.json; pc-run-lean-comparison.json.
- source-track-mode-copy-disassembly.txt; source-track-child-dispatch-disassembly.txt; source-clip-buffer-dispatcher-disassembly.txt; source-reference-track-vtable-constructor-disassembly.txt; source-base-track-constructor-disassembly.txt.
- pc-run-lean-unity.log; pc-run-lean-render.log; pc-run-lean-delivery-validation.json.

Canonical files in F:/DisneyInfinityPortalTest/ElsaSceneResearch, mirrored under Disney Reloaded/Tools/ExecutableResearch/DressResearch.
