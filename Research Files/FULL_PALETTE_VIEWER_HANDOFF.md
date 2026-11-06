# Full-palette viewer control — 2026-10-22

Update: the rebuilt viewer also accepts the tested diagonal-right and sideways-right run profiles. See FULL_PALETTE_DIRECTIONAL_HANDOFF.md. Earlier forward-only limits below describe the initial checkpoint.

Launch using `F:/DisneyInfinityPortalTest/OctaneCharacterViewer/Launch_Viewer.cmd`. It now prefers the separately built `bin/FullPalettePreview` application; prior builds are preserved.

Check **Full palette (tested Elsa profiles)**, then choose **Preview native clip (.oct)**. The checkbox passes the four opt-in source-path flags to evaluate_native_clip.py. Supported full-palette profiles are PC Elsa idles and class_girl forward walk/run. Uncheck it for established partial diagonal/sideways profiles. The checkbox starts unchecked; loading saved evaluated JSON retains that file's recorded coverage.

The setting controls the next selected-native preview, not the separate legacy re-evaluation button. It does not request an idle state transition; the prepared specific-idle comparison artifacts retain their separately configured explicit transition fixtures.

The option is disabled during baking with the existing backend controls. Unsupported/failed evaluations retain the existing preview. Successful full-palette output is checked for62 source nodes and zero fallback parents before loading. Status reports source coverage independently of the selected checkbox.

Build: `dotnet build OctaneCharacterViewer/OctaneCharacterViewer.csproj -c Release -o OctaneCharacterViewer/bin/FullPalettePreview --no-restore` passes with zero warnings/errors.

End-to-end hidden viewer smoke run with `--smoke-test --selected-native-smoke-test --full-palette` completed successfully. It generated a fresh forward-run bake, loaded19 samples and recorded `62 source-driven / 0 fallback` in selected-native-preview-smoke.json. Existing animation-import checks also pass. The generic renderer self-test reloads its standard pose inventory, so its screenshot is not evidence of a full-palette game comparison.

The final rebuild also gives both checkbox labels light text for the dark background. Complete palette coverage remains distinct from complete engine reconstruction or live-game parity; the known running-index-finger issue is unchanged.
