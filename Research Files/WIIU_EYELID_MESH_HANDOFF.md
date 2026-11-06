# Partial eyelid mesh diagnostic

Open eyelid-preview.html in a browser. Select bind pose or one of three clip snapshots. Drag to orbit, use the wheel to zoom, and toggle the affected-face highlight. No external web libraries or server are needed.

Source: Wii U fro_elsa.zip, decoded by copies of the current AssetWiiUdio mesh, palette, weight and archive readers. The exporter writes decoded OCT/buffers only into this diagnostic directory. Source game files remain unchanged. Copied source fingerprints are recorded.

The original 5,419 vertices all have normalized skin weights. 235 vertices carry one or more eyelid influences. Only those four influences receive evaluated skin matrices; 5,184 other vertices remain exactly at bind coordinates across all three snapshots. Reflected mesh coordinates use R * skin * R. Assertions check finite outputs, weight sums and unchanged non-lid vertices.

This is a partial-palette diagnostic, not full character playback. The four absolute world matrices include head motion while the rest stays at bind pose, so seams or offsets against the fixed face can occur. Such artifacts do not independently identify a decoder error. Plain material colors and highlighted affected triangles are diagnostic rendering, not source textures. No interpolation between samples or production viewer changes.

Rebuild from the workspace root:
```
dotnet run --project WiiUResearch/AnimationViewerResearch/EyelidDiagnostic -- WiiUResearch/EngineFormatResearch/PackageValidation/fro_elsa.zip WiiUResearch/AnimationViewerResearch/EyelidDiagnostic/Extracted
python WiiUResearch/AnimationViewerResearch/build_eyelid_diagnostic.py
```

Next useful improvement: evaluate the head influence and its dependent face influences consistently, or offer an explicitly labeled head-relative diagnostic. Then compare the rendered result before expanding to the full palette.
