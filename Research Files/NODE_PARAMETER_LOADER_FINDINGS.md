# Animation-state EaseDuration loader â€” 2026-10-21

The duration field observed in the live node block is populated by the XML animation-state parser as `p:EaseDuration`. This establishes a named file property and a constructor argument path, not a raw on-disk copy of the runtime block.

## Executable evidence

The parser enumerates `AnimTreeState` (string1DB2C08). At144CEAC..144CEE3 it looks up `p:EaseDuration` (string1DB2B9C), then its `value` attribute, converts the text through12C1C7D, and stores it at the parser frame+0xC8. The absent-field default is -1, loaded from float constant1B24120 and stored at144CCEC, with stack displacement accounting for the two pushed lookup arguments. The adjacent144CCE4 byte store is a separate flag, not this float. This corrects the earlier note's default0 interpretation; the explicit3 captured value is unaffected.

Original144CF53..144CFC8 packs that local into constructor argument12. Constructor1446650 reads it at1446683 and stores parameter-block+14 at1446692. Getter1441CD0 later returns precisely that field. The native selection and caller forwarding already verified in the live capture convert this parameter to seconds and pass it to the negative-duration fallback.

The constructor's1446704..1446724 loop hashes argument3, the clip string, by hash=hash*33+signed byte. ASCII IDLE_BREAKA/B/C produce8DB1FC43/44/45. The parser loads p:Clip into its frame+0x38, forwards it as argument3, and the constructor stores this hash at block+0. The separate state-name hash is constructor argument1 and is stored at block+0x28. These identifiers must not be conflated. The reader only supports ASCII identifiers and does not assert non-ASCII equivalence.

`test_node_parameter_loader.py` executes original argument-packing and constructor-store windows for -1,0,3,7, and the original identifier loop for all three names. All seven checks pass. XML lookup, text conversion and the entire allocating constructor are not replayed; the parsed locals are explicit synthetic inputs. Instruction evidence is saved in node-parameter-loader-disassembly.txt.

## Extracted file evidence

Installed `assets/gamedb/animtree_includes/basicmobility.animtree` is Snipe XML, not a mesh/ClipData binary. Its passive IdleA/B/C states reference IDLE_BREAKA/B/C and each specifies EaseDuration3. A fourth matching state is retained by the reader rather than silently discarded. The decoded installed Elsa BENT associates those aliases with specific01/02/03 motion files.

For IDLE_BREAKC, alias hash8DB1FC45 and EaseDuration3 agree with the live specific03 capture. This is a consistent shared-file candidate. We have not proved that the specific live instance was loaded from this exact XML file rather than another included/compiled representation. The prior failed binary search excluded .animtree files and cannot be interpreted as evidence that the property is absent from the installation.

Reusable reader: ElsaSceneResearch/read_idle_state_parameters.py. It records the XML SHA256, full state paths, fields, duplicate candidates and BENT motion aliases. Report: ControllerState/shared-idle-state-parameters.json.

## Next boundary

We can now obtain the duration from a named file property instead of inventing a universal0.1-second default. Next, connect the selected state to the viewer's explicit transition sequence and compare its produced factor with the recorded game transition. Keep that sequence labeled as explicit playback; the full automatic branch/event scheduler and runtime XML provenance remain separate work. No pose offsets or finger corrections were added.
