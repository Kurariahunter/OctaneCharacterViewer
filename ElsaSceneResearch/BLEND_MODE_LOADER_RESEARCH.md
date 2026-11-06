# Blend-mode loader research: verified boundaries and remaining link

Updated 2026-10-17. This checkpoint adds executable evidence and repeatable offline tests. No Unity animation, mesh, weights, game files or live game memory were changed.

## Result

We have separately established the source property normalization and one runtime contributor-flag selection path. We have NOT yet established that the source property's destination object is transferred into the runtime network flag or clip-mode field. Do not join those two observations into a claimed complete additive-blending pipeline.

Executable identity: DisneyInfinity3.exe SHA256 `f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705`. All addresses below are preferred-image virtual addresses in that build.

## Evidence ledger

| Observation | Evidence level | Boundary |
| --- | --- | --- |
| Source name BlendMethod at 0x1b4c2dc; loader0x780770 | Disassembly traced | Names a loaded property, not its full math semantics |
| Loader writes normalized boolean to destination+8 at0x7807df | Native instruction-window tested | External property lookup/type responses are synthetic |
| Caller0x780900 and reference caller0x781e70 invoke common loader | Disassembly traced | Call adjacency alone does not prove later object ownership |
| Runtime reference setup at0x7824b0 selects contributor flag at0x782658..0x78268b | Native window tested | Clip resolution and invalidation callbacks explicitly stubbed |
| Network getter0x4b1150 returns bit0 of network+0x18 | Native tested as part of selection window | Network field is not yet tied to track property |
| Clip getter0x5253b0 returns whether clip+0x44 equals integer1 | Native tested as part of selection window | Exact comparison; not arbitrary nonzero normalization |
| Runtime writes controller+0x39 only when value changes, then calls0x4bcc00 | Native window tested, callback counted | Callback internals were not executed by this test |
| Blend executor0x4e35d0 reads contributor flag+0x39 and separates flagged contributions | Prior + current disassembly | Type dispatch, mode transfer and numerical composition remain unverified |

## 1. Source loader: what is actually read

Function0x780770 receives a property source and destination. When both required lookup conditions succeed it requests BlendMethod through0x1826cf0. The property object's virtual type getter must return3, and its subtype field at+0x20 must also equal3 before raw+0x18 is accepted.

The accepted raw value is normalized:

```text
accepted raw value == 0  -> destination+8 = 0
accepted raw value != 0  -> destination+8 = 1
missing/rejected property -> destination+8 = 0
```

The loader does not preserve a multi-valued integer enum at this destination. Tested accepted values include0,1,2 and-1. This supports a binary mode distinction; it does not establish quaternion order or the words additive/override for the actual runtime operation.

### Correction discovered by testing

A first fixture hypothesis allowed subtype0 as well as3 because the disassembly contains a test for zero. Native execution rejected subtype0: it reaches a subsequent comparison against3 and takes the fallback. The test expectation was corrected to subtype3 only. This rejected hypothesis is recorded here rather than silently presented as an original fact.

## 2. Runtime flag selection: exact precedence

At0x782658, the runtime reference-controller path does this:

```text
if controller+0x70 points to a network:
    flag = uint32(network+0x18) & 1       # getter0x4b1150
else:
    clip = resolve controller clip      # call0x7700e0
    flag = (uint32(clip+0x44) == 1) if clip else 0

if controller.byte[0x39] != flag:
    controller.byte[0x39] = flag
    call0x4bcc00(controller)
```

The network branch has precedence even if a clip exists. A network field2 gives flag0;3 gives flag1. On the clip fallback, field1 gives true while field2 gives false. Thus neither branch is equivalent to the loader's general nonzero normalization.

This is a meaningful reason not to copy source BlendMethod directly to an assumed runtime field without tracing the intervening conversion.

## 3. Repeatable native tests

Script: `test_pc_blend_loader_windows.py`

Report: `pc-blend-loader-validation.json`

The script uses the existing hash-pinned PE memory image in Unicorn. It executes original instruction windows, not a Python reimplementation of those branches.

- Loader window:0x780796 through0x7807e2. Eleven cases cover accepted raw values, rejected type/subtype and missing property.
- Runtime selection window:0x782658 through0x78268b. Forty cases cover five network states (absent,0,1,2,3), four clip states (absent,0,1,2), and initial controller flag0/1.
- Every case requires reaching the specified stop address and matching its expected output. Callback counts must also match whether the flag changed.

Explicit fixtures/stubs:

1. Property lookup return is supplied at the call site0x7807a3.
2. Synthetic property virtual getter returns the requested test type.
3. Clip resolver return is supplied at call site0x78266a.
4. Invalidation callback0x4bcc00 is skipped and counted.

The real network getter and clip-mode getter execute unmodified in the emulator. The test does not run the whole loader, real property parser, asset resolver, controller lifecycle or invalidation callback. It does not prove that the real lean track reaches these exact objects in a running actor.

Reproduce from F:/DisneyInfinityPortalTest/ElsaSceneResearch with the configured Python runtime/dependencies:

```powershell
python test_pc_blend_loader_windows.py
```

Expected checkpoint:11 loader cases and40 flag cases pass. No running game required.

## 4. Object-layout caution

There are multiple objects with a field at+8. An offset is not a type name.

- The source loader's destination+8 is the normalized mode described above.
- Accessor0x76cc50 returns a64-byte row from a bounded table using owner+0x24, index+0x28, table+0x24 and count+0x28.
- Accessor0x76d1a0 follows object+0x78 into that row accessor.
- One consumer0x774500 treats row+8 as a string-like pointer while resolving weights. It must not be assumed to be the loader destination with its boolean+8 field merely because both paths concern tracks.
- Accessor0x19368d0 returns object+0x50; callers use that as a separate clip/controller-related object.

These are disassembly facts about the observed paths, not fully recovered C++ class declarations. The different ownership/layouts require an explicit constructor/copy/binding trace before being joined.

## 5. What is still missing

1. Establish the destination object's identity for an actual ReferencedTrack carrying BlendMethod1.
2. Trace how that object is stored/bound and whether its normalized+8 value changes a network bit, clip mode, different wrapper flag, or another mode field.
3. Identify the blend executor selected for each actual control type, not merely reuse the historical diagnostic name DilationBlend_4e35d0.
4. Replay native numerical blending using noncommuting rotations, identity deltas, differing translations, weights0/0.5/1 and order permutations. Verify reference-pose subtraction and scale behavior if present.
5. Independently compare against a matched running-game contributor capture; record effective weights, active source linkage and completed output stamps.
6. Only then apply lean offsets and create a separate Unity comparison preview.

The current static lean reader already supplies body, head and shoulder-spin channels, but those overlap the animated run. Simple field replacement is wrong for an additive layer. A guessed multiplication order could look plausible while contradicting native behavior.

## Files and provenance

Canonical: F:/DisneyInfinityPortalTest/ElsaSceneResearch.
Mirror: C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch.

- test_pc_blend_loader_windows.py; pc-blend-loader-validation.json.
- blend-property-loader-disassembly.txt.
- blend-runtime-flag-selection-disassembly.txt.
- blend-network-flag-getter-disassembly.txt; blend-clip-mode-getter-disassembly.txt.
- blend-config-row-getter-disassembly.txt; blend-source-row-accessor-disassembly.txt.
- blend-controller-getter-disassembly.txt.
- blend-loader-common-caller-disassembly.txt; blend-loader-reference-caller-disassembly.txt.
- blend-reference-controller-setup-disassembly.txt; blend-runtime-invalidation-disassembly.txt.
- blend-loader-callers.txt and blend-row-accessor-callers.txt are candidate-scan context: some windows begin before a recovered instruction boundary. Use the function-start-aligned disassemblies above for evidence, not accidental instructions in those leading bytes.

This note extends PC_RUN_LEAN_HANDOFF.md. It does not claim that lean blending is ready for production.
## First live Cheat Engine capture — 20:32:45

Capture ce_blend_20261017_203245_309480546.jsonl, SHA256 c7ad73c8931123a655001a4992ee08cf6db4d0fe785208adcdb745635d09fd57. Clean90-second time-limit stop.65runtime events across8controller addresses,0loader events. Preferred-image addresses were relocated against module base0x00de0000; actual runtime breakpoint0x0116267c.

All65events have consistent controller dump fields, ESI controller pointer, BL selected flag, sequential event numbers and breakpoint EIP.60network-branch events all agree with network+18 bit0 (55false,5true). Five null-network events have selected flag0; the captured +74 candidate is not sufficient to verify the actual fallback clip getter. No runtime event has old_flag39 different from selected_flag: this dataset captures existing mode selections, not a change notification.

No source-loader events occurred during this capture window. This does not prove the loader is unused; configuration may already have been loaded/cached before attachment, or the tested scene activity may not trigger this path. The current capture cannot connect the BlendMethod source property to the runtime controller, identify the actor, or establish numerical additive blending.

Next useful acquisition should target earlier content loading with the logger already active, rather than only repeat locomotion after content is loaded. If ordinary reloads still yield no loader events, trace the actual property-load timing/path before choosing another breakpoint. Do not infer that another identical walking capture will supply missing loader evidence.

Analyzer: OctaneLiveInspector/CheatEngine/analyze_blend_log.py. Full report beside the capture with suffix _analysis.json. Live debugger callbacks and JSON output now demonstrated; timing/actor/causal-pairing limitations remain.

## Hotkey live capture — 20:41:01

ce_blend_20261017_204101_309976671.jsonl SHA2568bd4cf54e2ef48e09b99ca39a12fa58f974c52c63bec882850723638b5515c05.47runtime events,0loader events; clean manual F9 stop. Observations span344–23829ms after capture start.44network-branch selections all match bit0;3null-network events remain unverified at the resolved-clip boundary. No old/new flag differences. Capture is structurally consistent and demonstrates manual-stop operation, not the missing loader-to-runtime transfer.

Two consecutive live captures have no source-loader hits. Repeating the same runtime capture does not resolve that boundary. Next investigate initialization/property-load timing or instrument an independently verified runtime mode/constructor boundary. No conclusion that cached asset loading is the sole cause; no blend semantics inferred from unchanged flags.

## First completed blend-execution capture — 20:46:31

Capture ce_blendexec_20261017_204631_310307171.jsonl, SHA256410b992654ecdd059f1a096d67cc793b40449070ab919263161e064bec0b38ed.120events across45processor addresses,63–282ms after F8; event limit stopped capture. This is about219ms of observed event span, not15seconds of motion or120independent frames.

All120output producer aliases match the recovered processor. Stack+1c processor recovery agrees. All120output8float payloads agree exactly numerically with the post-setter stack accumulator. This validates the chosen capture boundary and field recovery; it is not independent replay of the blend formula.

Contribution counts:56single,48double,5triple,11empty. The logger marks11empty tables as a boundary/rejected event because table pointer is null; their output aliases and accumulator/output comparison are valid. They are not evidence of broken animation data. No captured nonempty input has an accessor/slot boundary.167contribution records resolve through verified container methods and bounded slots.

56single unflagged unit-effective-weight cases reproduce the first8source payload values exactly in the output.52flagged contribution records include34with zero table-weight-times-factor2c and18positive-weight records. All18positive-weight flagged rotors are near identity: maximum component deviation5.572103418671759e-6. The visibly nonidentity flagged values in this capture have zero effective weight. Therefore this dataset does not discriminate noncommuting additive rotation order or prove the static run lean layer is active. No actor/clip identification was captured.

The next productive step is build a native blend-accumulator replay using these captured numeric fixtures, then controlled noncommuting rotations and weights, before generating another Unity preview. If another live capture is needed for active lean, use selective acquisition; an unfiltered120event capture fills in a fraction of a second and is not an adequate long movement recording.

Analyzer: OctaneLiveInspector/CheatEngine/analyze_blend_execution.py. Report beside capture with suffix _analysis.json. Earlier204101boundary log was already analyzed and is retained as a separate dataset; it is not joined to this capture by assumed thread/frame pairing.


## Native replay checkpoint

Original0x4e35d0executor reproduces109nonempty captured outputs exactly under explicit full-replacement/no-default-network fixtures.36controlled noncommuting cases distinguish weighted_delta*base from base*weighted_delta for base-first/flagged-delta-second table order. Reversing the table changes the result; sign/order diagnostics retained. Source mode transfer and clip identity remain unresolved. See PC_NATIVE_BLEND_REPLAY_HANDOFF.md for conditions, limitations and reproduction.
