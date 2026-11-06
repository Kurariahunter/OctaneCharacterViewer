# PC dress matrix converter capture prepared

2026-10-17. Live matrix capture/comparison pending. Local/world capture and existing validation remain available.

## Executable and correct PC source mapping

Original registered type stringProcessorNode::TransformToMatrix4x4VariantProcessorat0x1b30f54is referenced by registration0x501c8a, factory0x4f8180, allocation helper0x4eb520and constructor0x4df180. Constructor installs vtable0x1b2f5e4; execute slot+64points to0x55da50. The installed executable remains hash pinned.

Correct PC model SHA25638ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141ddeclares:

- dressLeftStart: worldTransform699 -> matrix698 via processor434.
- dressRightStart: worldTransform715 -> matrix714 via processor444.

Both matrix paths are source SkinInfluence associations for those exact weighted bones. Audit:pc-dress-matrix-source-audit.json. This establishes source association, not live renderer consumption.

## Runtime layout and capture

Native0x55da50uses direct typed input/output pointers atprocessor+0x18/+0x1C. It reads a Transform input and writes12floats to the output node starting at+0x40through+0x6C, not16floats at+0x34. The packed output is9linear values followed by3translation values. Native point correspondence isp[k]=sum(m[j*3+k]*v[j])+m[9+k]. Do not treat the12values as an ordinary row-major3x4matrix or infer a raw16-float Unity matrix.

The existing bounded downstream discovery now includes this converter's verified execute signature. An accepted matrix path requires exactly1converter consuming the exact verified world output, and an output node whose producer points back to that converter. Missing/ambiguous matrix paths remain explicit boundaries; local/world fallback is retained. Every sample revalidates links and captures exactly48matrix payload bytes at+0x40with raw header, float values and payload-offset metadata. Existing frame windows bracket these matrix reads too.

Summary now includes verified_matrix_paths. The same Capture Dress Skin Transforms.cmd collects the extra payloads. No additional game scan is introduced; its existing consumer scan includes the extra vtable signature.

## Native adapter and validation

native_pc_skin_matrix.pyexecutes original0x55da50in Unicorn using synthetic typed input/output references and the correct aligned output offset. validate_pc_matrix_converter.pytests48mixed-axis quaternion/translation/nonuniform-positive-scale cases against native point0x4c4350:240point comparisons, maximum coordinate error5.364418029785156e-07. A wrong-transpose control reaches2.4967246055603027, demonstrating the test detects layout errors.

The capture fixture tests cover matrix discovery, exact typed links, wrong output alias, changed input link and output offset0x40. Bytes at+0x34are deliberately nonfinite in the fixture to ensure they are not mistaken for the matrix payload. Existing discovery/dynamics/upstream/legacyIK/PCIKtests pass.

validate_pc_local_dress_transform.pyaccepts optional live matrix outputs and compares native conversion from predicted worldTransform and separately from capturedworldTransform. Results retain both component errors. It rejects an unexpected matrix width/offset and exits unsuccessfully on nonzero predicted-matrix error. No live matrix equality is claimed yet; existing captures do not contain those new fields.

## Run and next analysis

Run F:/DisneyInfinityPortalTest/OctaneLiveInspector/Capture Dress Skin Transforms.cmd with Elsa active. Return to the game during the5second delay and keep her moving/turning without changing scenes for about90seconds while scans/capture finish. Send the generatedJSONor its matching dynamics summary. Then check verified_matrix_paths, per-sample errors, completed/matching-frame stamps and native packed-matrix equality before any final skin claim.

The reader remains read-only: no writes, hooks, injection or pause. Captures remain non-atomic; converter outputs alone do not prove actual renderer palette consumption. No Unity animation assets changed in this increment.
