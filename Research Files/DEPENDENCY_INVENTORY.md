# Character-preview dependency inventory

Static dependency reachability for all62 PC Elsa skin influences, not proof every path is implemented or executed

Current bake:46/62 source-driven palette bones. Static whole-skin closure: 707 nodes, 421 processors, 47 processor types.

## Remaining fallback bones

- BrowLeft: node781 — `Anchor|BrowLeft|Transform|BrowLeft to WorldBasis`
- BrowCenter: node774 — `Anchor|BrowCenter|Transform|BrowCenter to WorldBasis`
- BrowRight: node788 — `Anchor|BrowRight|Transform|BrowRight to WorldBasis`
- CornerLipLeft: node723 — `Anchor|CornerLipLeft|Transform|CornerLipLeft to WorldBasis`
- CornerLipRight: node734 — `Anchor|CornerLipRight|Transform|CornerLipRight to WorldBasis`
- Jaw: node745 — `Anchor|Jaw|Transform|Jaw to WorldBasis`
- LowerLidLeft: node831 — `Anchor|LowerLidLeft|Transform|In WorldBasis`
- LowerLidRight: node828 — `Anchor|LowerLidRight|Transform|In WorldBasis`
- LowerLip: node752 — `Anchor|LowerLip|Transform|LowerLip to WorldBasis`
- UpperLidLeft: node825 — `Anchor|UpperLidLeft|Transform|In WorldBasis`
- UpperLidRight: node822 — `Anchor|UpperLidRight|Transform|In WorldBasis`
- UpperLip: node763 — `Anchor|UpperLip|Transform|UpperLip to WorldBasis`
- eyeLeft: node795 — `Anchor|eyeLeft|Transform|In WorldBasis`
- eyeRight: node809 — `Anchor|eyeRight|Transform|In WorldBasis`
- Forearm_OL_Right: node514 — `Anchor|Forearm_OL_Right|Transform|In WorldBasis`
- Forearm_OL_Left: node507 — `Anchor|Forearm_OL_Left|Transform|In WorldBasis`

## Processor types in the full skin closure

Counts below describe static reachability, not implementation status. Existing evaluator deliberately rejects unsupported paths.

| Processor type | Count |
|---|---:|
| AimConstraintProcessorNode | 8 |
| ConcatenateChainDilation | 76 |
| ConcatenateChainInverseDilation | 15 |
| ConcatenateChainInverseTransform | 4 |
| ConcatenateChainTransform | 23 |
| ConcatenateDilationTransform | 48 |
| ConcatenateInverseDilationTransform | 2 |
| ConcatenateInverseTransformDilation | 8 |
| ConcatenateTransformDilation | 8 |
| DilationComponentProcessorCompose | 16 |
| DilationComponentProcessorDecompose | 12 |
| DilationOrientationConnection | 12 |
| DilationTranslationOrientationConnection | 18 |
| DynamicChain | 3 |
| EulerZXYComponentProcessorCompose | 3 |
| EulerZXYComponentProcessorDecompose | 2 |
| EulerZXYToRotorVariantProcessor | 3 |
| FloatConnection | 2 |
| FloatMultiply | 2 |
| FloatNegate | 1 |
| IkLean2LinkProcessor | 2 |
| InverseTransformPositionWithTransform | 4 |
| InverseTransformVectorWithTransform | 3 |
| InvertConcatenateChainDilation | 3 |
| InvertConcatenateChainTransform | 4 |
| InvertDilation | 16 |
| InvertTransform | 2 |
| Position3dConnection | 2 |
| Position3dDifferenceProcessor | 11 |
| RelationshipProcessor | 8 |
| RotorToEulerZXYVariantProcessor | 2 |
| ScaleConnection | 2 |
| ShrinkingVolumeScaleZ | 2 |
| TransformComponentProcessorCompose | 6 |
| TransformComponentProcessorDecompose | 6 |
| TransformDilationWithDilation | 13 |
| TransformDilationWithTransform | 29 |
| TransformPositionWithDilation | 2 |
| TransformPositionWithTransform | 1 |
| TransformTransformWithDilation | 5 |
| TransformTransformWithTransform | 6 |
| TransformTranslationOrientationConnection | 8 |
| TransformTranslationOrientationScaleConnection | 8 |
| TransformVectorWithDilation | 2 |
| UnitRotor3dConnection | 4 |
| UnitRotor3dOffsetProcessor | 2 |
| UnitRotor3dWeightedAverageProcessor | 2 |

## Reconstructed versus substituted behavior

- Source identity, mapping tables, decoded tracks, mesh weights and inverse binds are file-derived.
- Curve, rotation, selected blend, relationship, IK, transform and chain routines are executed offline from the installed EXE. Native function fixtures supply object headers, cached numeric inputs and type metadata.
- The graph is evaluated by our bounded Python dispatcher, not the complete original network scheduler.
- Four source run layers/control sets are selected explicitly. Full game state-machine decisions and runtime layer composition are not reconstructed.
- Gravity, settling duration and in-place root behavior are fixture choices. Exact game contacts, forces and update order remain unresolved.
- Dress and braid feedback conventions are reconstructed; braid needs a synchronized live-game reference.
- Manual finger adjustments remain separate preview diagnostics and are absent from standalone raw playback.

## Next live-game capture request

No new broad Cheat Engine scan is needed to open this prototype. Before requesting captures, map these fields to stable verified addresses and identify the player actor:

1. Active clip identifiers, local times, weights, blend modes and control values for one steady run.
2. Final62 skin palettes plus frame/timestamp and actor identity.
3. Chain548 input anchor/container/constraint, force, previous local orientation, output positions and type tags in the same frames.
4. A short idle-to-run transition and a steady run segment.

Do not treat an arbitrary controller event as Elsa without actor identity. Existing captures and logger limits remain relevant. Only read/copy data for this research; no gameplay values need to be patched.

## Completion milestones

1. Independent viewer with original mesh and native-evaluated cached poses (this prototype).
2. Backend input/output contract, cancellation, diagnostics and generic clip selection within validated formats.
3. Match recorded game palettes at known clip times and layer state.
4. Remove fixture dependencies incrementally; support another complete clip and another character.
5. Only then investigate direct original loader/scheduler execution with correct object constructors, allocation, type registration and external-service stubs.

A complete game engine is outside this milestone. Rendering uses WPF, not the original engine renderer. Raw binary asset import still uses a one-time Unity mesh export bridge; normal viewer playback and evaluator refresh do not require Unity.

## Creator references

See ANIMATION_SYSTEM_REFERENCES.md for creator descriptions of filtered weapon-pose layering and shared procedural/full-body systems. These inform filter/layer capture priorities; no new binary-decoder claims follow from the descriptions.


## Source composition verification

See SOURCE_COMPOSITION_CHECKPOINT.md and source-composition.json. Matching PC forward-run declaration sequence now checked before native evaluation. Native samples unchanged. Full original filter resolution and active layer composition remain unresolved.
