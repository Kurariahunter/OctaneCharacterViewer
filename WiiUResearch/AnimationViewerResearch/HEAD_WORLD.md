# Wii U Head-world dependency replay — 2026-10-24

## Completed bounded fixture

Source Head-world data node388 depends on72source nodes. A narrow replay evaluates43processors per sample, uses authored clip controls and explicitly records15stored-default leaves. The root relationship at source node41 is344bytes; field-aware endian conversion is byte-identical to the existing PC data (SHA-2568093efdf1d301e42983bd039ff3ec265f5a5ca975db9f6f38894833c0ce5f4b5).

Three snapshots at0,2.5333333015441895 and5.066666603088379 produce finite, moving head-world matrices. Maximum matrix component movement relative to the first sample is0.32263825833797455; this is a movement measurement, not an error score.

The replay uses original-PC numerical operators through the existing offline harness: source relationship data, chain Dilation composition/inversion, orientation connections, raw Transform composition, Dilation/Transform concatenation and point transforms. The source input arrays and inverse-input counts come from the Wii U graph. Source Rotor offsets are retained. The EulerZXY variant encountered here is explicitly bounded to zero angles; a nonzero unverified case fails.

This is not native Wii U machine-code execution, complete actor initialization or runtime scheduling. Source defaults are fixtures, not demonstrated live values; raw clip interiors retain approximate Python time arithmetic. The working PC viewer is unchanged.

## Important correction to previous local-eyelid checkpoint

Nodes272,276,280,284 store identity Dilation data but have actual producers153,155,157,159. Each producer is ConcatenateChainDilation, combining its own rest/basis input with267. Therefore stored identity does NOT prove evaluated converter identity.

The earlier wiiu-eyelid-local-outputs.json is now explicitly labeled historical stored-value fixture. Its original-PC relationship and orientation-connection arithmetic remains bounded evidence, but the outputs must NOT be combined with the evaluated head-world transform as if the entire eyelid graph were complete.

This is exactly why the dependency walk was needed. No game asset, animation angle or tolerance was changed to conceal this discrepancy. The head evaluator rejects unverified TransformDilationWithDilation, rather than accepting a stored-identity substitution. It currently exports head-world only.

## Next missing operation

Resolve TransformDilationWithDilation against original code and fixtures with nonidentity converters. Determine its exact orientation/translation/scale behavior before inserting the generated converters. Then finish four eyelid world transforms and check their source Matrix4x4 associations. Do not assume ordinary matrix concatenation simply from the processor name.

## Reproduce

From project root:

```
python WiiUResearch/AnimationViewerResearch/transcode_eyelid_relationship.py 41
python WiiUResearch/AnimationViewerResearch/transcode_eyelid_relationship.py 34
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_head_fixture.py
```

The transcoder now uses distinct filenames for root and eyelid relationships; writing one does not replace the other. Reports:relationship-41-endian-equivalence.json,wiiu-head-world-fixture.json. The original source and PC executable remain read-only.

## Follow-up: converter resolved

See EYELID_WORLD.md and wiiu-head-eyelid-world-fixture.json. The previously missing operation now passes 48 native PC fixtures and the four eyelid paths are evaluated at three times. Earlier descriptions above document the prior checkpoint.
