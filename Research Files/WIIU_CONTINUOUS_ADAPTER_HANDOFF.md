# Continuous Wii U control sampling through shared PC evaluator — 2026-10-24

Launch OctaneCharacterViewer/Launch_WiiU_Adapter.cmd again. It now prefers the separate bin/WiiUAdapterContinuous build and loads wiiu-controls-pc-reference-viewer-continuous.json. The previous three-snapshot cache/build remains available. Close the old window if it still displays only three snapshots.

The single supported Wii U Elsa ClipDataBlock is pinned by SHA-256122f5851199b14e14a05a87403c765566dd0873a49570bef872ec1c0f4072e51. WiiUClip validates its72flags0cubic curves,127registers, sequential timeline map and constants, transcodes numeric fields by width, and executes the existing original-PC curve and ReverseEulerZXY routines. This replaces the old approximate Python interior samples for this test. It does not execute the Wii U CPU code or reconstruct its actor clock. Source port/descriptor mappings remain the already-audited bounded profile; this is not a universal animation loader.

The adapter samples153times over0..5.066666603088379seconds (about30Hz). Each sample evaluates49matching output dependency closures using the unchanged PC DressEval/raw/finger routines. Common graph caches are shared within a frame, rather than rebuilding the same graph once per bone. Frames remain independently evaluated; excluded dynamic chains do not gain temporal state by sampling more often. The13PCreference fallbacks keep constant bind-relative transforms. The PC62-bone reference mesh remains explicit; the WiiU64-bone mesh and15different source outputs still require adaptation.

These are153source-curve evaluations, not interpolation between the previous three poses. Viewer playback selects the nearest cached source pose. There is no assumption that this fixed sampling schedule equals the game's runtime timing, transition scheduling or layering.

Validation:
- Build: zero warnings/errors.
- WPF --smoke-test --wiiu-adapter-smoke-test: exit0;153samples,5419vertices,62matrix entries per sample,49source outputs/13fallbacks. Existing animation-import rejection/recovery checks also pass.
- Cache-wide checks:153unique palettes, strictly increasing evenly spaced times, finite matrices, and maximum fallback-local drift4.440892098500626e-16.
- The23overlapping outputs retain endpoint comparisons against the earlier approximate source-graph fixture under the unchanged1e-5bound. Interior points intentionally use native curve arithmetic now, so they are not asserted bit-equal to the earlier approximate Python samples.

Reproduce from workspace root:
```
python WiiUResearch/AnimationViewerResearch/wiiu_clip_sampler.py
python WiiUResearch/AnimationViewerResearch/reuse_pc_evaluator.py --continuous
python WiiUResearch/AnimationViewerResearch/validate_continuous_adapter.py
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/WiiUAdapterContinuous --no-restore
OctaneCharacterViewer/bin/WiiUAdapterContinuous/OctaneCharacterViewer.exe --smoke-test --wiiu-adapter-smoke-test
```

Next: inspect the continuous result, then adapt the differing foot/ankle and temporal dress/hair paths without weakening the source-equivalence gates. No new game capture was needed for this step.
