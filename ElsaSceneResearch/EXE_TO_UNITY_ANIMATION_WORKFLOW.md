# Disney Infinity PC: from executable research to Unity animation

Research walkthrough and handoff — 2026-10-17

## 1. What we have actually built

We have a bounded research pipeline that reads supported original PC motion files, samples their control channels, evaluates supported parts of the matching character's procedural rig, and bakes the resulting skin-bone transforms into ordinary Unity AnimationClips.

The executable supplies implementations and evidence for math that was difficult to infer from the assets alone. We did not recover the complete engine source code. We disassembled selected machine-code routines and execute some of those original routines offline in an x86 emulator. Python reconstructs the surrounding data and supported graph evaluation.

The strongest current example is the installed-PC Elsa model, with idle, walking and running research previews. This is not yet a universal character/animation importer, complete game animation-state reconstruction, or reverse exporter back into Octane files.

```text
Original character archive
    -> extracted model and motion OCT files
    -> tuple records / ClipDataBlock / source rig graph
    -> curve sampling + static channels + source-port mapping
    -> supported procedural graph (IK, relationships, transforms, dress dynamics)
    -> final skin-world transforms / native packed matrices
    -> coordinate conversion + 62-bone Unity palette
    -> AnimationClip + AnimatorController + prefab + preview scene

Pinned PC EXE -> disassembly + offline native adapters ----^ 
Live game captures -> independent numeric checks ----------^
Original game recordings -> visual comparison ------------^
```

Numeric replay and visual comparison answer different questions. A routine can match its captured outputs while an incomplete set of animation layers still looks different from the game.

## 2. Freeze the identities first

Our executable is:

`F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/DisneyInfinity3.exe`

SHA256:

`f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705`

It is a 32-bit x86 PE. Addresses in this document are preferred-image virtual addresses, not file offsets. Another executable build can move code or change implementations. Live process addresses must be interpreted against the module mapping, not assumed to be portable pointers.

The verified installed-PC Elsa model OCT has SHA256:

`38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d`

Its archive is the installed game's `assets/characters/fro_elsa/fro_elsa.zip`. The converted Unity source is `Assets/DI3Converted/fro_elsa/fro_elsa_Rigged.prefab` in Disney Reloaded.

An earlier downloaded model belonged to a different asset family. In particular, its researched IK layout had 13 inputs / 4 outputs; the installed-PC solver used here has 8 inputs / 3 outputs. Mixing their mappings or fixtures creates plausible-looking but invalid results. Hashes and explicit layout checks prevent that.

## 3. How we identify useful code in the EXE

### Static inspection

The tools use `pefile` to read PE sections and map virtual addresses to bytes, and Capstone for x86 disassembly. Asset processor names and executable registration/type information give leads. We trace the chain from a registered type through its factory, constructor, vtable and execution function, then inspect input/output access and called helpers.

For example, the native matrix converter was traced through registration, allocation/construction and its vtable to execution at `0x55DA50`. This tied the function to the source graph's TransformToMatrix processor. It was not selected merely because it produced numbers resembling a matrix.

Disassembly tells us such things as calling convention, object offsets, pointer tables, field widths, branch selectors and output layout. It does not automatically reveal the complete semantic meaning of every input. Those meanings need asset-graph and runtime checks.

### Selected routine index

| Responsibility | Preferred-image VA | Current use |
| --- | --- | --- |
| Timed scalar curve sampling | `0x522CF0` | Execute original curve evaluator offline |
| Curve time quantization helper | `0x5232E1` | Explain uint16 time sampling and Python/native differences |
| Convention-2 Euler conversion | `0x40E180` | Produce source xyzw rotors from decoded angles |
| PC 8-input / 3-output leg IK | `0x5382F0` | Evaluate supported PC leg solver slots |
| Relationship processor | `0x54C9A0` | Supported relationship evaluation through dedicated adapters |
| Transform composition | `0x5303E0` | Build typed Transform payloads |
| Native point transform | `0x4C4350` | Check payload interpretation and transform points |
| Transform/dilation conversion | `0x4D7E90`, `0x4D82C0` | Preserve source scale-compensation behavior |
| Chain transform concatenation | `0x57E240` | Compose source transform paths |
| DynamicChain execution / reset / step | `0x4AE360`, `0x4ACAD0`, `0x4ACDB0` | Reproduce bounded dress dynamics |
| Aim constraint | `0x534380` | Convert dress alignment vectors to orientation |
| Transform-to-packed-matrix | `0x55DA50` | Recover final 12-float matrix output |

These are research entry points, not a complete API. An address being identified does not mean every branch or configuration is decoded.

## 4. Running original machine code offline

`native_pc_lean_ik.py` is a compact example of the harness pattern:

1. Check the executable SHA256.
2. Use `pefile` to obtain its memory-mapped image.
3. Create a Unicorn emulator in 32-bit x86 mode.
4. Map the PE image at its preferred image base.
5. Map separate scratch memory for a synthetic stack, processor objects, node payloads, pointer arrays and output buffers.
6. Fill only the object fields and metadata needed by the selected routine.
7. Set registers and arguments according to the traced calling convention. For the relevant thiscall routines, ECX holds the processor object and ESP points at our synthetic stack.
8. Put a sentinel return address on the stack; run from the native entry point with an instruction budget.
9. Require execution to reach that sentinel, read the documented output fields, and reject nonfinite or invalid results.

The harness does not start the game's full loader, renderer or animation state machine. It does not magically emulate every Windows API. The selected routines must be self-contained enough for the fixtures we construct. An invalid memory read or missing dependency is a research failure to investigate, not something to silence with arbitrary zero-filled data.

Two fixture styles are useful:

- Captured-input replay: reconstruct a routine's inputs from a live observation, then compare its predicted output with the separately captured output.
- Numeric adapter: once the layout is established, accept ordinary numbers, build synthetic objects and call the same routine without needing a live process or captured object headers.

The second form is what lets file-only exports become reproducible. Native adapters remain dependent on this local executable during research baking. The generated Unity clips do not need it at playback time.

## 5. Reading animation data from the assets

QuickBMS and the Disney Infinity BMS script unpack the original archive into a separate research folder. This stage only exposes assets; it does not decode animation semantics.

`TupleDecoderResearch/decode_tup_safe.py` reads the OCT tuple records. The motion reader locates its ClipDataBlock; the model reader locates the matching SubNetwork, DataNodes, processor links and header/name information.

`pc_clip_decoder.py` validates the supported PC packed layout:

- Header and duration, bounded curve count and ordered offsets.
- Register/command block, curve blocks and float pool.
- Packed uint16 command words: high 3 bits give descriptor count; low 13 bits identify the source port.
- Static descriptors and timed descriptors, preserving their component types.
- Curve time ranges, component metadata, uint16 knots and signed-short coefficients.
- Bounds, finite values, supported opcodes and supported flag patterns.

Quantized coefficients are reconstructed using their recorded bias/scale and cumulative deltas. The independent Python sampler follows the supported knot and polynomial layout.

A crucial correction was time quantization: the original code converts time into uint16 ticks using float32 arithmetic and truncation before lookup. A smooth continuous-time approximation looked reasonable but disagreed on steep curves. Reproducing this reduced the PC idle comparison from roughly 0.022 raw channel units to below 0.000001.

The current walk/run reader accepts tested boundary flags `0`, `0x02` and `0x12`. Native sampling is used for export. Our tests of the independent Python implementation cover stated in-range times; they do not establish every out-of-range boundary behavior.

`read_pc_idle_files.py` combines constants and timed channel values. Rotation commands can refer to dynamic scalar registers or the static float pool, using the traced convention selector. Our supported rotation path calls original convention-2 Euler conversion. Source rotor conventions are not interchangeable with an unqualified `Quaternion.Euler` call in Unity.

## 6. Mapping curves to controls, then controls to bones

A motion channel normally targets a rig control, not necessarily a final render bone. The model supplies the bridge.

The PC Rig reader validates these uint16 mapping arrays:

`LocalUsedDataNodeIndices -> ConnectionMapUsedDataNodes`

with `LocalToPortIndices` and `PortToLocalIndices` checked in both directions. Header layout/string tables supply readable paths. Unmapped ports are kept explicit with no invented destination.

`pc_graph_controls.py` applies supported component values to leaf control fields. It preserves stored defaults, applies full-vector and component channels, and does not overwrite computed graph outputs as though they were independent controls.

Then the evaluator follows the source processor graph. Depending on the output, that can include rotor offsets, relationship curves, leg IK, dilation/transform conversions, scale compensation, dress anchors, DynamicChain integration, Aim constraints and final skin transforms.

Typed payloads matter. A source Transform's 16 floats are not a flat 4x4 matrix: they include rotor, translation, uniform scale and Scale/Unscale fields. Flattening that early or letting Unity multiply a different parent scale can break the legs or clothing.

State matters too. The dress solver carries particle state across frames; the corrected Aim stage initializes from the previous local output rotor and feeds its computed rotor into the next update. Resetting each frame or re-seeding from the next observed game state hides integration errors.

For walking/running, the animation definition `grl_bm_walkrun.banm` identifies lower-body, upper-body and separate lean tracks. The exported lower/upper tracks target disjoint mapped nodes and can be combined without guessing an overlapping blend. The lean layer remains excluded pending its blend semantics. Running also authors nonuniform scale on lower-dress controls 644/650; our run path preserves it through native typed transforms rather than discarding it.

## 7. How we decide what is known and what is still unknown

### Layer A: structural checks

Require valid extents, offsets, opcode shapes, mapping reversibility, expected source identities, finite values and supported graph operators. Unsupported formats fail explicitly. A parser accepting a file only proves that it fits those supported checks.

### Layer B: independent curve math versus original sampler

Sample the same original curve bytes at selected times with both the Python decoder and the original routine. Compare each component and record maximum error, source hash, sample times and flags.

Current examples:

| Dataset | Cases | Maximum absolute difference |
| --- | ---: | ---: |
| PC idle scalar curves | 276 | `9.230572821650185e-7` |
| Lower run curves | 96 | `1.7550858188997154e-6` |
| Upper run curves | 72 | `5.4942933314094944e-8` |

These are raw scalar errors, not degrees or final vertex distances. Invalid/truncated input and unknown-flag rejection tests are separate checks. Agreement is strong evidence for those samples, not proof of all possible curves.

### Layer C: native operator checks

Test the function with controlled inputs and independently check invariants: quaternion normalization/sign equivalence, IK endpoint position, transform points, matrix orientation, segment length and root constraints. Deliberately wrong alternatives can help distinguish conventions. Matching two calculations that share the same wrong assumption is insufficient.

### Layer D: read-only live game captures

`OctaneLiveInspector` reads the running process. It checks executable identity, known type/vtable execution paths, input/output counts, pointer relationships and producer aliases. Connected, updating instances are distinguished from inactive/template-shaped objects.

The inspector records inputs, cached outputs, parameters and frame stamps. These reads are not atomic. Frame values are read around the window; changing, incomplete, repeated or gapped samples are filtered according to the validator's stated criteria. We do not interpolate missing solver updates and call them captured evidence.

First replay one update using captured inputs/state. Then test consecutive runs: seed once, carry our own predicted state forward, and compare with later observed outputs without correcting our state from them. Keep external captured inputs explicit. This isolates the solver from still-unknown upstream behavior.

Negative controls help: a zero-force dress replay should differ when gravity matters. Competing orientation timing or transform hypotheses should be compared against samples that actually distinguish them.

The corrected Aim adapter matched 217 accepted captured local-rotor observations, including 104 carried steps, with maximum component error 0.0. This uses replay-predicted particle positions and captured anchors. It does not prove the whole upstream actor graph.

The 19:02:33 matrix capture supplied 376 accepted completed snapshots, representing 360 distinct chain/frame pairs. Native matrix predictions matched all 376 converter outputs numerically; 104 incomplete snapshots were excluded. Not all accepted samples shared the separate dynamics read window. These are not 376 independent full animation updates.

One raw world-payload discrepancy was retained in reports: Scale.w differed until the original point consumer materialized its cached uniform value. Point and packed-matrix results then matched. We documented the discrepancy instead of hiding it with a tolerance.

### Layer E: original-game video

Video establishes gait, timing, pose shape, visible clipping and broad deformation. It cannot identify exact internal channel values. Compare the same character, gait and a useful camera angle before declaring a match.

The latest game reference shows running, while the previous Unity test was walking. A new run preview removes that mismatch. Original-game running also shows pronounced angular dress folding, but this alone does not prove our clothing output is identical.

For an unknown curve/operator, the practical loop is: preserve bytes and provenance, locate its consumer, trace its layout/branches, capture a discriminating input/output example, build a bounded native fixture, compare independent predictions, then integrate it into the graph and test the final skin. Unknowns stay visible until evidence resolves them.

## 8. Converting evaluated output into Unity animation

### Bake final skin transforms

The Python bakers sample source controls and evaluate the supported graph at 60 Hz. Dress state persists; current locomotion bakes settle the initial pose for 120 ticks. Output poses are retained at 30 Hz. The run preview contains four 0.6-second cycles, 2.4 seconds total and 73 exported samples including the endpoint.

There are 62 original skin palette bones. Current previews evaluate 31 source-driven output paths; remaining bones inherit bind-relative offsets. That fallback is explicit and is not full facial/finger decoding.

For Transform outputs, `native_pc_skin_matrix.py` calls `0x55DA50`. The converter writes 12 floats at output node `+0x40`, not a guessed 16-float matrix at `+0x34`. Nine values encode the linear part and three encode translation. We expand them to a 4x4 matrix and compare transformed points. Dilation paths retain their supported evaluator route.

### Convert coordinate conventions

The current exporter uses a reflection `R = diag(-1,1,1,1)` and transforms each source world matrix as:

`M_unity = R * M_source * R`

This is specific to this established import basis. It is not a universal fix for every game or FBX. Validate against the original mesh and inverse bind matrices.

### Create the AnimationClip

The Unity Editor builder loads the original prefab, retains the original skin mesh/weights/bind poses/materials and flattens the 62 palette bones under the animated root. Since the exported poses are world transforms relative to that root, independent palette bones avoid unwanted parent-scale compounding.

For every bone/sample it decomposes the converted matrix into position, quaternion and scale, rejecting nonfinite, singular, reflected or materially sheared results. Quaternion signs are kept continuous between keys; q and -q represent the same orientation but should not cause interpolation flips.

It writes ten Transform curves per bone:

- `m_LocalPosition.x/y/z`
- `m_LocalRotation.x/y/z/w`
- `m_LocalScale.x/y/z`

That is 620 bindings for 62 bones. The builder sets key tangents to linear, calls `EnsureQuaternionContinuity`, saves the `.anim`, creates an AnimatorController, assigns it to a prefab, and creates front/side preview instances.

The clips are ordinary baked Transform animation. They are not automatically Humanoid-retargetable. Playback no longer runs the Octane solver; its sampled result is already in the clip. The current preview plays once and holds; a seamless loop and gameplay root movement are separate work.

### Verify the saved Unity result

We build first in the isolated validation project, then:

1. Reconstruct TRS matrices from sampled Unity curves and compare with exported matrices.
2. Check finite skinned vertices and measurable motion.
3. Instantiate a freshly saved prefab and confirm its Animator actually changes a bone.
4. Check binding count and palette bone references.
5. Render several poses for visual inspection. The isolated render helper uses CPU linear-blend skinning when checking visuals, avoiding a stale headless skin result.
6. Save a fresh scene referencing original materials; temporary render materials/helpers are not delivered.
7. Copy into a new production preview folder and verify asset GUID references resolve.

For the run bake: ankle error was at most `3.6737498418666874e-6`, dress root error 0, segment-length error at most `2.149825033548325e-7`, and 3,915 native matrix/point comparisons differed by at most `2.384185791015625e-7`. Unity's reconstructed matrix error was at most `4.470348e-7`. These validate the stated stages, not complete original-game fidelity.

## 9. Reproduce the current checkpoint

Canonical scripts and reports live in:

`F:/DisneyInfinityPortalTest/ElsaSceneResearch`

Research mirror:

`C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch`

The scripts currently contain machine-specific paths. Use the configured Python runtime with pefile, capstone, unicorn and numpy available; keep the pinned EXE and extracted source assets at their expected locations.

From the canonical research folder:

```powershell
python test_pc_file_reader.py
python test_pc_run_file_reader.py
python test_pc_upper_run_file_reader.py
python bake_pc_run.py
```

The bake writes `pc-run-animation.json` and `pc-run-validation.json`. It does not itself import assets into Unity. The Unity builder reads its copy of that JSON under `Assets/DI3PCRunPreview/Editor/Data/`.

The builder's batch entry point is `DI3PCRunPreview.Batch`. It refuses to overwrite an existing Generated folder. Run it only in a prepared validation copy with a new output location; do not delete an existing preview merely to reproduce a result. The isolated-only render entry point was `DI3PCRunRender.Run`.

Current delivered scene:

`C:/Users/Kurar/Disney Reloaded/Assets/DI3PCRunPreview/Generated/Elsa_PC_Run_Preview.unity`

## 10. File guide and remaining work

| File or area | Responsibility |
| --- | --- |
| `pc_clip_decoder.py` | Supported packed commands, quantized curve structure and independent sampling |
| `read_pc_idle_files.py` | Rig mapping, constants, typed channels and file-only native sampling |
| `native_pc_clip_math.py` | Original curve and Euler routines |
| `native_pc_lean_ik.py` | Pinned PE image and PC 8/3 IK adapter |
| `pc_graph_controls.py` | Apply supported leaf-control fields |
| `evaluate_pc_arms.py`, `evaluate_pc_legs.py` | Supported procedural skeleton graph |
| `evaluate_pc_raw_transform.py` | Typed native Transform propagation |
| `native_pc_transform_scale.py` | Compose, concatenate and point operations with scale state |
| `native_pc_chain_step.py` | Persistent dress-chain state |
| `evaluate_pc_feedback_dress.py` | Prior-output Aim feedback correction |
| `native_pc_skin_matrix.py` | Native packed matrix converter |
| `pc_skin_palette.py` | Source skin associations and bind-relative fallback palette |
| `bake_pc_run.py` | File-driven lower/upper run controls through the graph to sampled skin poses |
| `validate_pc_feedback_evaluator.py` | Captured local-rotor comparisons |
| `validate_pc_local_dress_transform.py` | Local/world/matrix capture validation |
| `OctaneLiveInspector` | Read-only process capture tools and capture JSONs |
| `DI3PCRunPreview.cs` | Unity clip, controller, prefab and preview creation |
| `PC_RUN_HANDOFF.md` | Latest run checkpoint and limitations |

Still unresolved or partial: full actor-layer blending, the separate lean layer, unmapped template ports, full facial/finger behavior, all graph operators and all characters, exact game-scene forces/collisions/update scheduling, renderer palette upload verification, seamless looping, and conversion back into original game animation files.

The repeatable method is to establish one boundary at a time: bytes to channels, channels to controls, controls through native graph operations, graph output to skin matrices, then matrices to Unity curves. Each boundary needs its own evidence; a good-looking preview alone cannot substitute for that chain.
