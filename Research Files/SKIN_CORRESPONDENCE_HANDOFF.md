# Source/export skin correspondence

Audit: ElsaSceneResearch/audit_viewer_skin_correspondence.py. Report: skin-correspondence-validation.json.

All 62 exported bone names and their order match the OCT Influence order and the preserved original Unity mesh audit. Every named influence resolves through the source SkinInfluence association into the palette's world-data node. No missing or duplicate bone names were found.

All 5419 exported vertices correspond to the preserved mesh audit (maximum coordinate difference 5.876922615222213e-8); triangle order matches exactly. Bone indices and weight values match that audit exactly. Weight sums differ from 1 by at most 4.516914486885071e-8. 906 vertices have a positive Thumb/Index/Middle influence. This comparison uses the preserved Unity audit for mesh streams, not a fresh raw VBUF decode; it cannot independently validate every importer stream-layout decision.

## Bind-pose difference explained

Comparing reflected OCT inverse-bind matrices directly with exported bind matrices shows a maximum component difference about .000648. It is not localized to fingers. For each bone compute C = inverse(source inverse-bind) * exported inverse-bind. All 62 C values agree with the Body-derived common transform within 8.858863832506003e-7. The common transform is essentially a Y translation of +.0006480814, with ordinary float decomposition/rounding residuals.

Importer code provides the relevant coordinate policy: DI3AssetBuilder.cs shifts mesh vertices by groundOffset; DI3RigReader.Attach shifts bone worlds by the same amount and rebuilds bind poses from those transforms. Therefore a common mesh-space bind offset is expected. Do not remove it from bind matrices alone: shifted vertices and their bind matrices must be treated together. Raw VBUF positions were not freshly decoded in this task, so this is source-code consistency plus measured common-transform evidence, not a new end-to-end importer proof.

Exported bind matrices also match the preserved original Unity audit within 1e-6 per element. No finger-only bone-order, index, weight or bind discrepancy was identified. No mesh, bind pose, influence, hierarchy or animation value was changed.

## Next comparison

Live relationship-local idle outputs are already exact; selected hierarchy math and CPU skinning pass independent checks. The remaining gap is correspondence with the game's final hand/finger world matrices, including unchecked connection/conversion paths and any active run-specific layers. Trace those final native matrix outputs rather than adding corrective offsets. A targeted world-matrix capture may be required once its mapping to the verified relationship/skin association is established.
