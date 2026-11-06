# Disney Infinity 3.0 executable research reference

Updated: 2026-10-15. Consolidates the locally recorded Yoda/Elsa executable investigation through the native leg IK demonstration. It is an evidence reference, not a claim that the complete animation format or engine has been reconstructed.

## 1. Current result

The executable has supplied verified implementations for timed curve evaluation, one Euler rotation convention, rotor offset order, a dilation conversion, and Elsa's configured two-bone leg IK routine. We can generate partial Unity AnimationClips from sampled final bone transforms. We cannot yet reconstruct a complete original Elsa idle, all characters, or a reversible animation exporter.

The original leg solver reaches controlled synthetic targets. Elsa's original foot-target graph is still undecoded. Do not confuse the stick-leg demonstration with recovered original animation.

### Evidence levels

- **Native tested:** isolated execution of original machine code, with stated inputs and checks.
- **Disassembly traced:** registration, dispatch, field access or call path identified in this executable; not necessarily a complete runtime behavior test.
- **Asset/graph corroborated:** matches source records, boundaries, bind matrices or graph structure; not independent execution of the complete original loader.
- **Unity tested:** compilation, generated asset playback, matrix/skinning checks or inspected render; does not by itself establish original-game fidelity.
- **Unresolved:** no supported implementation or insufficient discriminating evidence.

## 2. Executable identity and address conventions

| Item | Value |
|---|---|
| Local executable | `F:\Games\Disney Infinity - Gold Collection\Disney Infinity 3.0\DisneyInfinity3.exe` |
| SHA256 | `f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705` |
| Analysis architecture | 32-bit x86 PE |
| Method | Read-only PE disassembly and isolated Unicorn emulation of selected routines |
| Libraries | `pefile`, `capstone`, `unicorn`, `numpy` |

Addresses below are preferred-image **virtual addresses**, not file offsets. They are specific to the pinned executable. `exe_reader.py` resolves PE sections when reading a VA. Do not apply these addresses to another release, console executable or different hash without tracing it again.

The native harnesses map a PE memory image and construct minimal objects, node payloads, stack and metadata. They do not launch the game or run its complete asset-loading/state-machine pipeline. Original game files were not modified. Unity playback of the generated clips does not need the executable; research resampling currently does.

## 3. Address index

| Feature | Address / chain | Status |
|---|---|---|
| Animation command interpreter region | `0x532371` | Disassembly traced |
| Rotation command branch | `0x5323A9â€“0x532479` | Disassembly traced |
| Euler dispatch call | `0x532431 -> 0x52B120` | Disassembly traced |
| Convention-2 Euler conversion | `0x40E180` | Native tested |
| Timed curve evaluator | `0x522CF0` | Native tested |
| Scalar command branch, low nibble A | `0x532693` | Disassembly traced |
| Rotor offset registration / factory | `0x501F7A -> 0x4F2FF0` | Disassembly traced |
| Rotor offset vtable / execution | `0x1B2D3AC`, slot 16 -> `0x4C18B0 -> 0x4BD400` | Native tested math |
| Dilation conversion registration / factory | push at `0x501B39` (operand `0x501B3A`) -> `0x4D70C0` | Disassembly traced |
| Dilation conversion constructor / vtable / execution | `0x4B74E0 -> 0x1B2CA74`, slot 16 -> `0x4D7440` | Native tested |
| Squash-Z two-bone IK registration / factory | `0x50211B -> 0x54B880` | Disassembly traced |
| IK wrapper / allocation-configuration helper | `0x54B850 -> 0x545F40` | Disassembly traced |
| IK RTTI vtable / execution | `0x1B343EC`, slot 16 -> `0x53B620` | Native tested configured fixture |
| IK internal call sites | `0x525A30`, `0x53ABF0` | Calls observed; not independently decoded here |
| Foot RelationshipProcessor registration / factory / runtime | `0x5020CD -> 0x5568B0`; vtable `0x1B349AC`, slot 16 -> `0x54C9A0` | Runtime traced; table accessors native-tested, evaluation unresolved |
| Node payload getter / rotor setter | `0x48D2B0`, `0x48D2E0` | Field accesses traced |
| Dilation payload setter | `0x4B1E70` | Field accesses traced |
| IK output-slot lookup | `0x527F20` | Field accesses traced |

An address being listed does not imply that the complete function, all branches, or all types are understood.

## 4. Animation command interpretation

### Rotation family

The `0x1xxx` records in the traced interpreter advance by **8 bytes**: a uint16 opcode and three uint16 operands.

```text
axis source flags: (opcode >> shift) & 3, for shifts 4, 2, 0
Euler convention:  (opcode >> 6) & 7
```

Flag value1 selects a dynamic scalar register in the traced branch. The other branch uses an alternate base previously identified as the static float pool; current bounded samplers accept only tested flags0/1. Do not assign meanings to flags2/3 merely because the interpreter takes the alternate branch.

`0x1081`, `0x1084` and `0x1095` select convention2. `0x1095` selects dynamic X/Y/Z. The traced call dispatches through `0x52B120` to `0x40E180`.

### Convention-2 formula

With angles in radians, let `sx=sin(x/2)`, `cx=cos(x/2)`, and similarly for Y and Z. Source quaternion order is xyzw:

```text
qx = -(cy*sx*cz + sy*cx*sz)
qy = -(sy*cx*cz - cy*sx*sz)
qz = -(cy*cx*sz - sy*sx*cz)
qw =  cy*cx*cz + sy*sx*sz
```

Our source quaternion-to-matrix function is the transpose of the conventional quaternion matrix. Under that convention the conversion gives `Ry @ Rx @ Rz`. Do not copy signs/order into Unity's Quaternion.Euler without accounting for the conventions.

Six diagnostic mixed/individual-axis cases matched the original routine within `7.2874e-8` per quaternion component. Earlier Yoda work records421 head samples within `1.24e-7`. This verifies the traced convention, not every Euler selector or eyelid decoding rule.

### Scalar records and unresolved flag

All 87 on-disk records carrying flag`0x10` across six inspected Elsa idle samples target Float DataNodes and contain descriptor`0x001A`. The runtime low-nibble-A branch resolves a compatible node and writes a scalar at object`+0x34`.

This supports scalar-control classification. It does **not** fully resolve the on-disk flag's lifetime/loading meaning. Preserve the flag. The historical Elsa interleaved on-disk format differs from the packed port/count words in the traced runtime loop; that conversion path is still unresolved.

## 5. Timed curve evaluation

`0x522CF0` is the original curve evaluator used as a reference. Research sampling feeds original curve bytes and a time into isolated execution and checks completion and finite outputs.

| Corpus | Recorded test result | Interpretation |
|---|---|---|
| Earlier Yoda samples |324 curve/component-group cases; Python approximation differs by up to roughly0.000744 raw units | Approximation is not bit-exact |
| Elsa active/passive idle |276 cases; max Python/native difference `0.02203720834135936` raw units | Native sampling is used in current previews |

These differences are raw channel values, not degrees or Unity positions. Do not equate finite output with complete animation correctness.

Asset-derived supported layout observations, **not all independently proven by EXE tracing**:

- Animated header uint16 at`+10` supplies curve count in supported samples; offset table starts at`+12`.
- Table contains float-pool, command-block and curve offsets. Register entries identify curve/component sources.
- Supported timed curve headers contain component-kind and segment-quantity fields plus start/end times; component metadata provides quantization parameters.
- Supported segment knots are uint16 normalized to65535; signed-short coefficients are reconstructed cumulatively. The Python cubic approximation remains less accurate than native evaluation.
- Elsa active idle is approximately 4.2s, 28 curve blocks, 50 registers; passive is approximately 6.166667s, 18 blocks, 45 registers.
- Current Elsa structural/continuity scan: 22/30 motion payloads pass supported checks, 1 more has a continuity warning, 7 unsupported. `elsa_bm_idle_specific02` has a 2353-quantization-unit discontinuity and is not validated.
- Six static facial samples were intentionally excluded by the animated-header reader; exclusion does not imply corruption.

These counts supersede historical 3/30 and 12/30 notes. Structural acceptance is not native full-motion playback validation.

## 6. Ports, controls and constant channels

Elsa asset evidence: 490 DataNodeLinks bytes, 90 non-FF links forming a permutation of 90 ConnectionMapUsedDataNodes slots. Candidate mapping:

```text
DataNodeLinks[port] -> used slot -> source DataNode
```

All 243 commands across six parsed idle samples resolve structurally. The complete original runtime loader mapping has not been independently executed.

| Input | Port | DataNode |
|---|---:|---:|
| Body group |16|207|
| Body |18|212|
| Hips |316|499|
| Spine1 |397|219|
| Spine2 |399|226|
| Spine3 |400|232|
| Neck |370|240|
| Head |308|246|
| Left shoulder spin / shoulder |392 /386|336 /341|
| Right shoulder spin / shoulder |393 /389|368 /373|
| Left foot / center |193 /202|37 /47|
| Right foot / center |201 /204|64 /74|
| Left / right knee controls |325 /326|703 /687|

These are procedural input controls, not final skin-bone transforms.

Historical Elsa constant-channel reader now consumes active 101 and passive 64 records at exact aligned boundaries 1496 and 1076. Selected constant translations/quaternions are applied before timed overrides. Bounds, finite values, quaternion length and table boundaries are checked.

Passive Spine2/Spine3 inputs have fixed rotations; their lack of timed movement is expected. Clip-local constants are **not** proof that complete BENT/base/additive layering has been decoded. Unknown selected commands or unsupported scale behavior are rejected.

## 7. Rotor offset multiplication

RTTI identifies the tested `CommonBasisArrayProcessor<UnitRotor3d, OffsetPolicy<...>>`. Authored operands are Input, Offset, Output. Original execution establishes:

```text
Hamilton xyzw: q_out = q_offset * q_input
source matrix: M_out = M_input @ M_offset
```

103 tests passed;101 distinguish opposite orders. Max quaternion component error `8.1276e-8`; source matrix error `2.5739e-7`.

Historical label **RIGHT** refers to source matrix order. It does not mean Hamilton multiplication in the same written order. Offset-order correctness does not validate old Head/Neck mappings or broad bind-relative corrections.

## 8. Dilation conversion and object-layout observations

For the tested `TransformDilationWithDilation` routine:

```text
M_output = M_converter @ M_input
```

100 deterministic original-code tests cover rotations, translations and positive uniform scales. Max matrix error `9.4216e-7`. Nonuniform/negative scales and every related transform processor are not covered.

Observed minimal harness fields, specific to the traced object layouts:

| Location | Observed use |
|---|---|
| Node`+0x34` | Start of numeric payload; scalar or quaternion depending on node type |
| Dilation`+0x34..0x40` | xyzw quaternion |
| Dilation`+0x44..0x4C` | xyz translation |
| Dilation`+0x50` | Uniform scale |
| Node`+0x1C` | Metadata/version pointer used by getter/setter |
| Node`+0x20` | Version stamp compared/copied by getter/setter |
| Typed operand checks via node`+0x10` | Type metadata in the tested dilation wrapper |
| IK processor`+0x18` | uint16 relative operand-array offset |
| IK processor`+0x1A / +0x1B` | Input/output counts |
| IK processor`+0x1C` | Configuration flags |

Metadata layouts differ by processor family. These are minimal test objects, not a complete ABI or asset serialization specification.

## 9. Correct skin-bone output mapping

**Critical correction:** `BasisRef` identifies a coordinate frame; it does not necessarily name the bone driven by a DataNode. Match graph outputs to local skin bind transforms.

| Skin bone | Correct output DataNode | Current status |
|---|---:|---|
| Body |102|Sampled|
| Spine1 / Spine2 / Spine3 |108 /114 /120|Sampled|
| Neck / Head |393 /398|Sampled|
| Clavicle left / right |126 /154|Sampled; constant local channels in tested idles|
| Shoulder spin left / right |131 /159|Sampled|
| Hips |410|Sampled via input499, converter498 and output502|
| Upper arm left / right |136 /164|Not applied: default rotation differs from skin bind by about 23 degrees|

Earlier previews incorrectly treated Head as407 and Neck as398, then used broad bind-relative rotation compensation. Those assets are preserved as historical diagnostics and superseded by the corrected torso/body tests. The independently verified offset multiplication order remains valid.

Corrected previews use source rotations directly. Explicit small local skin-pivot translation reconciliations remain: Spine1`0.0008869171`, hips`0.0007961988` model units. These adjustments are documented, not proof of exact original skin/runtime composition.

Reflection for current Unity conversion is `R=diag(-1,1,1,1)`, with `M_unity=R @ M_source @ R`. Source matrix layout/transposition must be handled before this reflection. No universal cross-platform conversion claim is made.

Some helper bone parents remain preview approximations. Original bind matrices are preserved, but complete runtime helper behavior is unverified.

## 10. Original two-bone leg IK

Processor name: `IK2BRPLengthSquashZConstraint`. Elsa source processor 408 drives one leg and 412 the other. Both authored NetworkBuffer words are 23; traced factory logic maps that to runtimeflags 30 (`0x1E`). Bit mapping is traced; detailed semantic names for every option are not fully established.

There are 13 input slots and 4 output slots. **Factory slots do not follow the authored DataNodeRefs order.** Reorder authored input indices as:

```text
[12, 2, 1, 10, 3, 8, 9, 7, 6, 5, 4, 0, 11]
```

| Runtime slot | Input |
|---:|---|
|0|Target translation|
|1|Pole vector|
|2|Twist|
|3|Start translation|
|4 /5 /6|Initial start /mid /end positions|
|7 /8|Initial start /mid local-to-parent orientations|
|9 /10|Initial start /mid local-to-start-parent orientations|
|11|Distance threshold|
|12|Scale multiplier|

Reorder internal output slots as `[1,0,3,2]` to obtain authored mid rotation, start rotation, mid scale, start scale.

### What was tested

- Direct execution of the original IK routine using both authored leg geometries.
- 200 deterministic reachable targets, fixed zero pole/twist and unit input scale.
- Finite, unit quaternion outputs; unit scales for those fixtures.
- Forward-kinematics ankle error at most `1.5106646745328471e-5` model units.
- Initial-target rotation matrix errors at most `2.2568660882349434e-6` against stored graph rotations.
- Fixed regression tolerance`5e-5` allows the measured numerical error; no bit-exact claim.
- Four-second controlled bend-cycle Unity demo; saved Animator playback and render checked.

The demo cycle's independently sampled maximum error differs slightly from the random-target set; its Unity report records roughly`1.97e-5`.

### What is not tested

Original animated foot-target reconstruction, other flag combinations, arbitrary character rigs, arbitrary poles/twist/scales, unreachable targets, squash edge cases, complete skin mapping and planted feet in Elsa's original idle.

This is original-code **emulation**, not yet a portable mathematical implementation ready for the production importer.

## 11. Foot-target graph and evaluator corrections

Original foot targets depend on `RelationshipProcessor` nodes 24/34. Inputs include foot/ball/toe controls and authored relationship data; outputs include several transforms. Registration/factory located at`0x5020CD -> 0x5568B0`; runtime is now located at `0x54C9A0`; complete evaluation/math remain undecoded.

Additional unresolved leg dependencies include `ConcatenateInverseTransformDilation`, `InvertConcatenateChainTransform`, `TransformDilationWithTransform`, `TransformPositionWithDilation`, `Position3dOffsetProcessor` and related scalar/basis operations. Do not implement these by names alone.

Producer discovery originally recognized only exact`Output` and component compose/decompose fields. It missed names such as`OutputRotation[0]`, `OutputScale[1]` and relationship`Output[n]`. That could silently substitute stored defaults or produce misleading self-cycles when following output dependencies.

Current discovery recognizes Output-prefixed attributes. Unsupported IK/Relationship processors fail explicitly before traversing their outputs. No fake knee/ankle curves are generated. The native IK test remains separate from the production graph evaluator until its real inputs are decoded.

Applying passive hip controls while leaving leg/dress controls fixed makes Elsa's skirt and feet swing off the grid. This is evidence of incomplete composition, not successful foot planting or independent proof that every pose mapping is correct.

## 12. Unity pipeline, tests and limits

```text
extracted scene/ClipDataBlock
  -> checked payload/command/constant parsing
  -> native curve and convention-2 controller sampling
  -> verified subset of procedural graph
  -> final local skin-bone transforms
  -> coordinate conversion and explicit pivot reconciliation
  -> Unity AnimationClip curves + AnimatorController + diagnostic prefab
```

Partial generated clips cover body, spine, neck, head, clavicle/shoulder-spin and hips. Current Elsa tests sample 30 Hz with linear Unity interpolation. Earlier Yoda head test sampled 60 Hz. Loop flags/interpolation do not establish seamless original-game loops.

Isolated Unity 6000.5.8f1 tests include compilation, bind reconstruction, sampled local matrices, finite skinned vertices, unchanged unrelated local transforms and fresh saved-prefab playback. Elsa bind error is about`2.58e-7`; sampled local matrix errors about`2.99e-7` or less in the tested previews. Those errors compare against our reconstructed data, not recorded original-game animation ground truth.

Copied live-project materials use URP. Live scene recording supports visual review; time-spaced frame inspection does not establish perfect continuous timing or loop seams. Research Editor-folder mesh/texture dependencies have not been packaged as build-ready assets.

The supported outcome is partial original-data-to-Unity animation. Reverse conversion back into original game files, a complete generic importer, BENT/state-machine reconstruction, additive/base layering and universal character support are **not implemented**.

## 13. Reproduction and evidence files

All executable harnesses must use the pinned local executable. Runtime dependencies were loaded from the existing analysis dependency directory under DI3ConverterValidation/YodaAnimationProbe; the scripts contain machine-specific paths. The native curve sampler also uses the existing Yoda research decoder. These are research scripts, not a standalone redistributable toolkit.

From `F:\DisneyInfinityPortalTest`, with the configured Python and dependencies:

```powershell
python ElsaSceneResearch/validate_elsa_native_curves.py
python ElsaSceneResearch/validate_rotor_offset_native.py
python ElsaSceneResearch/validate_dilation_native.py
python ElsaSceneResearch/native_leg_ik.py
```

These commands regenerate their research reports. They do not import or modify game data. `native_leg_ik.py` additionally writes controlled-demo samples. Unity demo/build methods create uniquely named research asset folders; they do not replace the original character prefab.

### Primary evidence index

| Evidence | Local file |
|---|---|
| Interpreter addresses, historical caveats |[executable-findings.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/executable-findings.json)|
| Runtime branch excerpts |[interpreter-disassembly.txt](F:/DisneyInfinityPortalTest/ElsaSceneResearch/interpreter-disassembly.txt), [command-loop-disassembly.txt](F:/DisneyInfinityPortalTest/ElsaSceneResearch/command-loop-disassembly.txt), [scalar-command-disassembly.txt](F:/DisneyInfinityPortalTest/ElsaSceneResearch/scalar-command-disassembly.txt)|
| Euler implementation and tests |[validate_native_rotation.py](F:/DisneyInfinityPortalTest/OctaneAnimationReference-20261014/research/timed-head/validate_native_rotation.py), [native-rotation-validation.json](F:/DisneyInfinityPortalTest/OctaneAnimationReference-20261014/research/timed-head/native-rotation-validation.json)|
| Curve reference |[validate_elsa_native_curves.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/validate_elsa_native_curves.py), [elsa-native-curve-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/elsa-native-curve-validation.json)|
| Named controller sampling |[sample_named_controls.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/sample_named_controls.py), [elsa-control-mapping.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/elsa-control-mapping.json)|
| Structural scan / constants |[timed-curve-comparison.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/timed-curve-comparison.json), [decode_elsa_static_channels.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/decode_elsa_static_channels.py)|
| Rotor offset |[validate_rotor_offset_native.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/validate_rotor_offset_native.py), [rotor-offset-native-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/rotor-offset-native-validation.json)|
| Dilation conversion |[validate_dilation_native.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/validate_dilation_native.py), [dilation-native-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/dilation-native-validation.json)|
| IK harness / tests |[native_leg_ik.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/native_leg_ik.py), [leg-ik-native-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/leg-ik-native-validation.json)|
| IK operands / code excerpt |[leg-ik-research.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/leg-ik-research.json), [ik-runtime-disassembly.txt](F:/DisneyInfinityPortalTest/ElsaSceneResearch/ik-runtime-disassembly.txt)|
| Relationship factory lead |[foot-relationship-lead.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/foot-relationship-lead.json)|
| Current bounded graph evaluator |[evaluate_elsa_head.py](F:/DisneyInfinityPortalTest/ElsaSceneResearch/evaluate_elsa_head.py)|
| Corrected mappings |[torso-mapping-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/torso-mapping-validation.json), [body-mapping-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/body-mapping-validation.json), [hips-mapping-validation.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/hips-mapping-validation.json)|
| Earlier Yoda context, including superseded early assumptions |[Yoda research README](<C:/Users/Kurar/Disney Reloaded/Tools/YodaTimedHeadResearch/README.md>)|

### Unity artifacts

- [Corrected torso/head comparison](<C:/Users/Kurar/Disney Reloaded/Assets/ElsaTorsoResearch/TorsoNativeDiagnostic/Elsa_TorsoComparison.prefab>)
- [Body/shoulder comparison](<C:/Users/Kurar/Disney Reloaded/Assets/ElsaBodyResearch/BodyShoulderDiagnostic/Elsa_BodyComparison.prefab>)
- [Hip-only-composition diagnostic with floor grid](<C:/Users/Kurar/Disney Reloaded/Assets/ElsaHipsResearch/HipsDiagnostic/Elsa_HipsComparison.prefab>)
- [Controlled native IK demonstration](<C:/Users/Kurar/Disney Reloaded/Assets/ElsaLegIKResearch/ControlledSolverDemo/NativeLegIK.prefab>)

Historical README/LATEST_FINDINGS/ROTOR_OFFSET_FINDINGS notes are chronological. Their statements that no Unity clips exist, old Head/Neck mappings, old acceptance counts or broad bind-relative rotation alignment are superseded by the specific corrections above. Keep them for provenance, not as current implementation instructions.

## 14. Next research steps

1. Trace RelationshipProcessor factory `0x5568B0` to its runtime and authored relationship data; reproduce original foot-target outputs.
2. Validate required basis/position conversions against original code. Preserve explicit rejection of unsupported types.
3. Feed original clip-derived target/pole/twist values into the verified IK configuration; test knee/ankle outputs and scale behavior over complete clips.
4. Resolve missing upper-leg/skin composition and dress controls; compare feet to a floor reference without hiding errors by manual pose adjustment.
5. Resolve upper-arm default rotation mismatch and remaining arm/hand/facial/helper behavior.
6. Decode base/additive and BENT selection/layering, then broaden the tested character/clip corpus.
7. Only then promote supported cases into the importer, with bounded parsing, diagnostics and unsupported-case rejection.

## 15. What this document does not establish

It does not establish that every `.ann`/`.bent` format is cracked, that mesh extraction alone recovers motion, that a third-party Blender animation importer already solves the problem, or that all Octane-named engines are related. It contains no verified new findings about NFC progression fields, AES archive keys, console executables or round-trip animation writing. Those are separate investigations.

## 16. Foot relationship trace follow-up (2026-10-15)

The processor runtime is now located: vtable `0x1B349AC`, execution slot 16 -> `0x54C9A0`. Its stages call record accessor `0x503E00`, input evaluator `0x544E00`, output writer `0x53D2B0`, and helper `0x53E920` (exact completion/cache semantics unresolved). Constructor `0x53CC90` allocates a base `0x68`-byte processor plus appended arrays.

Both feet share the same 580-byte RelationshipData blob. Native accessor checks confirm two sections separated by 228 bytes, one group, count pairs 4/4, and a second-section record list at blob offset 284 with count 4. This is metadata access only, not four recovered transforms or complete foot-target execution.

Detailed fields, address chain, reproducible probe and next steps: [FOOT_RELATIONSHIP_HANDOFF.md](F:/DisneyInfinityPortalTest/ElsaSceneResearch/FOOT_RELATIONSHIP_HANDOFF.md). Native-tested table report: [foot-relationship-structure.json](F:/DisneyInfinityPortalTest/ElsaSceneResearch/foot-relationship-structure.json).

Next trace: input record evaluation in `0x544E00` and output type/composition dispatch in `0x53D2B0`, then cache initialization and a complete neutral foot-control fixture. Previous character previews and production importer remain unchanged.

## Saved external file-inventory lead

[DI3_FILE_INVENTORY_REFERENCE.md](<C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DI3_FILE_INVENTORY_REFERENCE.md>) records the reviewed DI3ListOfAllFiles repository, inspected files, observed names, limitations and planned cross-version comparison. Large remote inventories have not yet been downloaded or compared.

## Cached community tool comparison (2026-10-15)

[Five-repository cache and comparison](<C:/Users/Kurar/Disney Reloaded/Tools/CommunityResearchCache/themadgoblin/README.md>):47 commit-pinned, hash-verified source/document/data files, including the full20MB texture-name dataset. Tools were inspected, not executed. Static mesh/export, texture lookup and disk-save packing findings are separate from unresolved original animation RelationshipProcessor math.

## 17. Foot relationship numeric evaluation follow-up (2026-10-15)

The original complete RelationshipProcessor `0x54C9A0` now executes on the shared Elsa foot blob in a minimal fixture. In 69 neutral/axis/mixed cases, complete and staged execution agree exactly. The four scalar controls produce independent source-X rotations, with signs +,-,+,- under our source matrix convention, zero translations and unit scale. Approximate input*pi/200 response differs from native by at most 0.000239732 radians; do not substitute the ideal formula for the quantized source behavior.

Active/passive idle foot scalars are all constant zero. Actual foot target movement still requires foot-group/center transforms, basis conversion, hip/leg IK and skin composition. No new original character animation or production importer support is claimed.

[Detailed current checkpoint](<C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/FootRelationship/FOOT_RELATIONSHIP_EVALUATION.md>) describes the minimal type/version fixture, reset-cache limitation, tested ranges and next dependencies. The earlier metadata-only handoff remains for provenance.

## 18. Original foot target graph follow-up (2026-10-15)

Six additional basis/scalar operators passed 360 original-code rigid-transform checks, maximum error about 4.30e-7. A separate Elsa-only evaluator now connects original idle foot transforms and the native relationship/IK routines. Active idle: 127 times, 254 ankle checks, maximum target-to-ankle error 7.58e-7 model units. This is graph/solver internal consistency, not final skin playback.

Passive idle requires nonuniform Scale/Unscale composition: 186 times expose up to 0.014943-unit error under ordinary matrix chaining. Do not claim planted feet or generate a final passive clip from those diagnostic matrices.

[Current target-graph handoff](<C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/FootRelationship/ORIGINAL_FOOT_TARGET_HANDOFF.md>) contains operator addresses, test scope, passive scale findings and the exact next trace at native Transform helper `0x4C2D50`. Existing Unity previews and production importer are unchanged.

## 19. Native nonuniform Transform fixture follow-up (2026-10-15)

Original component compose `0x5303E0`, point transform `0x4C4350` and concatenate `0x4C2D50` passed 500 Scale/Unscale fixtures, maximum error about 3.43e-7. Retaining native fields and explicitly setting child Unscale=parent Scale closes all 626 recorded active/passive endpoint checks to below 8.53e-7 model units. This verifies the fixture, not the original skin hierarchy's metadata assignment.

New original-idle-target stick-leg diagnostics are installed under Assets/ElsaOriginalLegResearch. Actual Elsa skin export remains pending hierarchy/upper-leg mapping. [Current Scale/Unscale handoff](<C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/FootRelationship/TRANSFORM_SCALE_HANDOFF.md>) records formulas, scope, tests and source-trace next steps.

## Native leg skin preview checkpoint


Research evaluator evaluate_native_skin.py now preserves original Transform payloads through the actual knee/ankle skin paths. Newly traced processor executes: InvertTransform0x4d1a60, ConcatenateChainTransform0x57e240, ConcatenateDilationTransform0x57cb30, ConcatenateTransformDilation0x4d0c50. Original constructors/vtables traced from registered factories. Existing native unit fixtures are reused; graph results below corroborate the specific Elsa paths, not arbitrary runtime loading.

Default evaluated knees differ from bind by about1cm. Substituting the authored stored upper/knee locals reduces maximum bind matrix difference to0.000849884. This supports distinguishing IK default pose from bind; no bind-relative rotation correction was applied. Retained original native IK output.

The earlier flattened evaluator made passive ankle-orientation data nonorthogonal. Reading native quaternion components through the Dilation/Transform conversions removes that artifact. Native UnitRotor offset order preserved. Real source output paths, without the earlier manual child-Unscale fixture, now reach original clip targets: active127frames/254ankles maxworlderror7.67518297414536e-7; passive186frames/372ankles maxworlderror9.548831781930068e-7. Hips/knees/ankles/ball/toe world transforms exported. Dilation/control dependencies still use bounded FootEval; full original graph loader/blending not executed.

Unity parent-relative matrices for the passive knee/ankle chain contain shear up to0.04746766 because the source carries independent scale metadata. Individual world matrices are TRS-compatible. A separate research preview therefore uses64 independent palette bones, retains original weights/inverse binds, and bakes world transforms to local curves under a common identity skeleton. The rest of the mesh follows the existing bounded torso preview; arms/face/skirt control decoding is incomplete. This is not a general retargetable rig.

Build and verify scripts: sample_skin_controls.py, validate_native_skin_clips.py, build_native_skin_preview_data.py, DI3ElsaNativeSkinPreview.cs. Evidence reports: native-skin-default-validation.json, native-skin-clip-validation.json, native-skin-export-validation.json, native-skin-delivery-validation.json.

Isolated Unity6000.5.8f1 validation passed. Bind mesh deformation error1.816246e-7; saved clip matrix reconstruction errors active4.768372e-7/passive4.172325e-7. Max skinned displacement active0.06352764/passive0.2114231. Both saved Animator instances move. Visual render inspected at2sec: passive feet remain down during body lean; undecoded skirt visibly follows older partial pose and requires further work.

Live output: Assets/ElsaNativeSkinResearch/NativeSkinDiagnostic/Elsa_NativeSkinComparison.prefab. Active/passive .anim files and controllers beside it. New editor menu: Tools/DI3 Static Converter/Research/Create Elsa Native Skin Preview. Delivered materials use existing reviewed URP counterparts; references checked against live project GUIDs. No production importer or prior prefabs replaced. Research textures still depend on Editor/Data and are not player-build-packaged.

Next useful decoding target: skirt/lower-dress proxy outputs, then arm channels. Rebuilding a conventional hierarchy requires representing native scale compensation rather than collapsing helpers or applying guessed bind corrections.


## Elsa dress / DynamicChain checkpoint
Source UpperDress outputs sampled into Assets/ElsaUpperDressResearch/UpperDressDiagnostic/Elsa_UpperDressComparison.prefab. Lower dress is DynamicChain simulation, not just another clip curve. Producer discovery now rejects unevaluated Position[...] simulation outputs instead of silently using stored zeros. Native reset passed60 transformed fixtures; native timestep awaits cached scene/capsule-parent linkage at processor+0x34. See DressResearch/DRESS_RESEARCH_HANDOFF.md for exact nodes, addresses, qualifications and reproduction. Lower-chain motion remains incomplete.


## Native DynamicChain dress stepping and exact header paths
Correction: prior capsule-parent diagnosis was incorrect; the factory literal is ^.Orientation and the cached reference is read as a quaternion. Full native dispatch now matches staged reset/step for120moving-anchor frames. HeaderLayout parent/count decoding resolves all64skin output associations, including19Dilation payloads previously excluded by terminal/type guesses. Native Aim/difference/inverse operators tested on100fixtures each. Both Elsa idle clips now drive bounded persistent lower-dress simulations (zero external force, reset start, explicit local-aim feedback);626side/frame samples preserve authored lengths/root positions. New independent preview Assets/ElsaDynamicDressResearch/DynamicDressDiagnostic/Elsa_DynamicDressComparison.prefab and .anim clips passed isolated Unity skin/clip checks. Full loader/update ordering and force defaults remain qualified. See DressResearch/NATIVE_DYNAMIC_DRESS_HANDOFF.md for complete evidence and reproduction.


## Skirt audit: missing authored knee scalar controls
Reset-only versus stepped counterfactual shows the active bulge exists before time stepping, not from accumulated integration instability. Audit found omitted constant Float ports189/197 (nodes43/70) feeding native IK twist; active values-.08/+.0790359974, passive0/1. Typed scalar sampling added and native legs/dress rebaked. All target, skin, curve and saved-Animator checks passed in isolated Unity; original weights/geometry/binds preserved. New preview Assets/ElsaKneeDressResearch/KneeDressDiagnostic/Elsa_KneeDressComparison.prefab. IMPORTANT: active skirt bulge remains; do not claim this fixes it. Next focus is static source pose/proxy/reference behavior, not speculative weight changes. See DressResearch/SKIRT_BULGE_KNEE_HANDOFF.md.


## Dress reference audit after Movie_013 (2026-10-16)
See DressResearch/DRESS_REFERENCE_AUDIT_HANDOFF.md. Three newly traced original Dilation operators pass 300 randomized fixtures plus 1878 source-node comparisons over all313 sampled frames (max3.56036e-7). Omitted controls on the traced dependency set match neutral clip values; no omitted timed records. Active bulge remains unresolved. No mesh, weights, preview or importer changes. Remaining boundary: full graph scheduling, animation layers and independent original-game pose reference.


## Elsa BENT declarations and scheduling audit (2026-10-16)
See DressResearch/ELSA_LAYER_SCHEDULE_HANDOFF.md. Inventoried27 channels,27 bases,441 file entries; stance clips have no explicit Layers/Filter overrides.611 processors/845 explicit dependency edges form a DAG. Adding cached dress Orientation references produces two4-processor feedback components, neither upstream of UpperDress650/655. DefaultData index/pool inventory retained without applying an unvalidated format. Runtime channel activation/default loading and blend semantics remain unresolved; no preview or production changes.


## Native connection defaults and channel declarations (2026-10-16)
See DressResearch/NATIVE_CHANNEL_DEFAULTS_HANDOFF.md. Original transform getter0x4b23d0 and scalar block0x4e33d0 confirm13-bit float-pool offsets.100 randomized transform/scalar pairs pass exactly; all90 Elsa defaults exactly equal stored fallback values. No default-value correction justified. BENT channel loader0x787480..0x787670 reads20-byte records, defaults priority0/weight1/index-1. Runtime layer activation, sort direction and complete blend semantics remain unresolved. Active skirt bulge remains; no preview or production changes.


## Live particle0.5 versus1 comparison (2026-10-16)
See DressResearch/LIVE_PARTICLE_COMPARISON_HANDOFF.md. Native comparison yields identical positions and skin matrices across313 source frames and120 moving-anchor frames. Arithmetic-block sensitivity test confirms slot98 can affect nonzero inputs under its flag-dependent branch. Captured three world-space and three identity chains uniquely match Elsa source hair/left/right parameter signatures; runtime ownership still qualified. Updated read-only capture includes5-second focus delay,60samples,LastFrame/reset and cached Orientation. No preview fix or new live capture claimed.


## Animated live lower-dress cross-check (2026-10-16)
See DressResearch/ANIMATED_LIVE_DRESS_HANDOFF.md.60live samples distinguish3updating chains(LastFrame within0..1 of global frame) from3inactive identity chains(LastFrame143). Original inverse/Aim calculation applied to live endpoints/anchor reproduces cached local Orientation: median0degrees each side,maxleft0.000002415degrees,right0.023329degrees. Non-atomic reads/large-world float precision qualified. Strong evidence for local lower-dress orientation calculation given inputs, not complete simulation or clip fidelity. Next: upstream UpperDress instance/control/clip-time mapping. No preview changes.


## Live upper-dress passive correspondence (2026-10-16)
See DressResearch/LIVE_UPPER_DRESS_HANDOFF.md. Output-alias-validated producer paths expose left/right upper-dress candidates0x1e073cdc/0x1e073e6c under common anchor0x1e06759c in captured process. Removing world placement gives39/60samples close to decoded passive poses; first sample rotation errors0.02734/0.00960degrees,translation7.16e-5/4.74e-5. No sampled pose closely matches decoded active. This supports passive output correspondence; it does not establish active decoding is wrong or identify runtime clip/time/layers. Unknown producer boundaries and instantiated graph topology remain. No preview changes.


## CRITICAL: installed Elsa differs from downloaded research asset (2026-10-17)
See DressResearch/INSTALLED_ELSA_VERSION_MISMATCH_HANDOFF.md. Connected live thigh producer is IkLean2LinkProcessor,vtable0x1b35744,execute0x5382f0,8inputs/3outputs. Read-only extraction of installed fro_elsa.oct confirms this declaration and SHA38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d, differing from downloaded research OCT126ec007bafe36a24799b30e56f57e4d58da15698607dcfc06097c580928f4d2(13/4IK2BRP). All6installed idle ClipDataBlocks also differ; BENT41522->65571bytes. Previous source-family validations preserved, not proof of identical current-PC assets. Original archive platform/version not established. Need installed graph/clip mapping and native8/3solver validation; enough offline assets extracted, no repeated identical stance capture required yet.

