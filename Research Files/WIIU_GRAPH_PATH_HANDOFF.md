# Wii U source graph to eyelid skin association — 2026-10-24

**Correction: converter nodes272/276/280/284 have upstream producers. The identity-converter local outputs below are limited stored-value fixtures, not completed graph outputs. See HEAD_WORLD.md before reusing them.**

Continuation of ROTATION.md. Research-only; existing PC viewer playback is unchanged.

## Strong cross-platform data equivalence

Wii U Elsa source RelationshipData node34 contains612bytes, SHA-256f93a2bbfc9a79d1a6a4b0821623a0eb7b9ad013f9a41ccef958d5077b2e2ada7. A field-aware endian conversion of stage headers, curve headers/metadata, knots, coefficients and16-bit command streams yields SHA-2567ad4d7ac5ad56a235376973be6fd8849ac5e68d27d1ece72d96d04a1f25216b3, exactly equal to the previously verified PC Elsa eyelid relationship. All612bytes match; no coefficients or offsets were fitted.

Wii U processor178 references this blob. Inputs are338,339,340,337 and outputs273,277,281,285. The existing PC processor177 uses different node IDs. Reuse the verified data semantics, not raw node-number assumptions. Existing PC bounded full-versus-staged relationship tests are documented in OctaneCharacterViewer/EYELID_GRAPH_HANDOFF.md.

## Four source paths

| Bone | Relationship output | Identity-converter output | Head-local orientation output | World Dilation output | Matrix output | Influence |
|---|---:|---:|---:|---:|---:|---:|
|LowerLidLeft|273|274|821|823|822|7|
|LowerLidRight|277|278|818|820|819|8|
|UpperLidLeft|281|282|827|829|828|10|
|UpperLidRight|285|286|824|826|825|11|

Each path runs TransformDilationWithDilation, DilationOrientationConnection, TransformDilationWithTransform using Head-world node388, then DilationToMatrix4x4VariantProcessor. The AssociationPool explicitly links each final Matrix4x4 node’s full header path to its Geometry4skin influence. These are source associations, not bone-name heuristics.

## Bounded evaluation performed

Three file-derived control samples supply the four independent lid scalar inputs. Original PC native RelationshipProcessor evaluates the byte-identical converted blob with explicit zero caches and identity initial outputs. Each following source converter is explicitly stored identity Dilation; no dynamic converter was replaced by a guess.

The original PC orientation-only connection is then called using the Wii U output node’s stored initial orientation/translation/scale, with identity optional rotation offset (the source processor declares no offset connection). It produces12finite unit-rotor head-local eyelid outputs, preserves each source translation within1e-7, and retains the source’s distinct left/right rest positions. This is tested PC numerical execution on equivalent relationship data plus source-derived connection fixtures, not native Wii U code execution or proof of complete initialization parity.

Outputs are in wiiu-eyelid-local-outputs.json. The script intentionally stops before Head-world node388, which has an upstream producer. It does not use that node’s stored identity value as an animated world transform. Consequently no complete world matrices, final palette or viewer animation is claimed.

Input curve values retain the earlier Python interior-time approximation. Numerical tests here validate graph/data routing and bounded native operators; they are not synchronized live-game measurements.

## Full source skin mapping

AssociationPool and DataNode header paths resolve all64unique Wii U Elsa influences to Matrix4x4 outputs. The earlier PC mesh has62influence names. The two Wii U additions are Ankle_Left and Ankle_Right; all62PC names are present. Preserve platform-specific palettes and use explicit associations: raw palette indexes/counts must not be copied between versions.

Artifacts:
- transcode_eyelid_relationship.py and eyelid-endian-equivalence.json
- evaluate_wiiu_eyelid_controls.py and wiiu-eyelid-local-outputs.json
- wiiu-skin-associations.json (64explicit source bindings)
- skin-name-platform-diff.json

Next: resolve the actual Head-world dependency chain from source controls, then apply the validated local eyelid outputs to it. Do not restart finger captures or add corrective pose offsets as part of this work.
