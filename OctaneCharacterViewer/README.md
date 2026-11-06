# Octane Character Viewer

An experimental Windows viewer for researching **Disney Infinity's native character rigs and animation data**, independent of Unity.

The project combines a **C# / .NET 10 WPF viewer** with Python decoding and evaluation research. Supported animation paths can be evaluated into skin-palette samples and played against a character mesh with CPU skinning.

**This is a research source snapshot, not a portable, ready-to-run release.** The source builds without game assets, but playback and native evaluation require separately prepared local files, configured paths, and backend dependencies. Game executables, extracted assets, and evaluated pose caches are not included.

## What it does

- Display a textured character mesh using weights and inverse bind matrices.
- Play, pause, restart, scrub, and step through evaluated animation samples.
- Orbit and zoom the preview.
- Load compatible evaluated animation JSON and select clips.
- Inspect supported native OCT clip channels through the Python backend.
- Evaluate specifically validated source profiles into preview palettes.
- Provide experimental PC/Wii U comparison and character-trial paths.
- Record diagnostic results for numerical and visual comparisons.

Support depends on the particular rig, clip, curve format, and graph processors. A successful test on one profile is not a claim that every character or animation is supported.

## What “native” means here

The research follows the game's original animation data and uses selected original executable routines through emulation, alongside reconstructed graph and timing logic. The C# rendering loop plays evaluated samples; it does not embed the full engine or continuously execute the original game.

The viewer is not a replacement for the game renderer, actor controller, animation scheduler, cloth solver, or collision system. Sampled playback and numerical agreement on individual functions do not establish complete in-game parity. Scrubbing does not reverse-simulate the engine.

## Requirements

- Windows and the [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) for building the viewer.
- A Python environment for backend operations. Included research uses packages such as NumPy and Unicorn; individual scripts may require additional analysis libraries.
- Your own compatible game executable and extracted character/animation assets where required by an evaluator.
- Locally prepared mesh JSON, textures, and evaluated pose JSON for playback.

There is currently no pinned, complete Python environment or automated first-run asset setup in this snapshot. Some scripts import local modules or read research fixtures that are not distributed here.

## Build

From the repository root:

```powershell
dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release
```

The Windows executable is generated under:

```text
OctaneCharacterViewer/bin/Release/net10.0-windows/
```

The C# project has no external NuGet package references. A successful build does not create the data needed for playback.

## Configuration before running

The current `Program.cs` contains workstation-specific `Root` and `NativePython` constants. Update these to your repository location and Python interpreter. Python profiles and backend scripts also contain source/fixture paths that need review.

The default viewer expects prepared files such as:

```text
OctaneCharacterViewer/Data/elsa-pc-mesh.json
OctaneCharacterViewer/NativePreviews/current-native-run.json
```

It can fall back to research outputs such as `ElsaSceneResearch/pc-run-braid-animation.json`. These are examples of expected local inputs, not files shipped in this repository. Review the model/pose structures in `Program.cs` and the evaluation scripts before preparing your own data. Different character trials use additional paths and model hashes.

`native-preview-profiles.json` is metadata describing validated clips and companion sources. It contains no animation payloads. Its workstation paths must be configured; a profile is not a substitute for the original files.

The original launcher selects among local research build folders. For a fresh source build, run the Release executable directly after configuration rather than relying on those historical build paths.

## Source-package layout

```text
OctaneCharacterViewer/                 WPF viewer, preview scripts, and research notes
ElsaSceneResearch/                     PC evaluator and native-math research scripts
WiiUResearch/AnimationViewerResearch/   Wii U adapter/evaluation research scripts
WiiUResearch/OCTParser/                BinaryTup inspection scripts
BlenderElsaImporter/di_oct_channels/    Shared scene/channel research modules
```

Sibling folders retain their relative layout because existing scripts resolve imports through it. Included analysis scripts are historical research tools, not a supported command-line product. Inspect script inputs before running them: some expect existing captures, generate fixtures, or access a locally configured game executable.

The ZIP excludes build output, virtual environments, captures, screenshots, extracted game resources, and generated pose data. Original historical notes are retained for context, but their coverage counts and “next steps” describe particular checkpoints, not universal current support.

## Known limitations

- Hardcoded paths, source hashes, and fixture dependencies remain.
- Native file preview is bounded to explicitly supported profiles; this is not a generic open-any-OCT player.
- Curve formats, graph processors, timing, layering, and runtime inputs are not fully reconstructed.
- Some research previews retain fallback bones or reference-rig adapters.
- Fingers, cloth, and other secondary deformation can differ from the game.
- No complete native animation editor/exporter or general round-trip OCT writer is provided by this viewer.
- Research scripts are not all necessary for playback and have not been certified as one reproducible end-to-end environment.

## Contributing

The most useful improvements are configurable paths, reproducible dependency setup, a documented asset preparation workflow, additional independently verified curve/processor support, and tests against known source and runtime samples.

When reporting problems, include the revision, source platform, character and clip, source hashes where possible, selected profile, and diagnostics. Distinguish parser failure, rig mapping, graph evaluation, timing, and rendering differences. Do not upload proprietary executables, game assets, or live process dumps to the repository.

## Credits

This project records ongoing Disney Infinity animation and file-format research. Preserve author attributions and licenses present in individual source files and referenced research.

Disney Infinity and its assets belong to their respective rights holders. This unofficial tool is not affiliated with or endorsed by Disney or Avalanche Software. “Octane” here refers to Avalanche's game-engine research, not OTOY's renderer.

## Source-package verification

The staged C# viewer built successfully in Release configuration on November 5, 2026, using .NET SDK 10.0.403: zero warnings and zero errors. This is a compilation check, not validation of the separately configured Python/data pipeline.
