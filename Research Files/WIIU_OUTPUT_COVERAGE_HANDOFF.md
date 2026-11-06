# Complete source-output coverage audit — 2026-10-24

Audited all 64 source skin associations against three control snapshots. 24 output paths execute using current bounded original-PC numerical helpers; 40 stop at explicit unsupported operations or restricted data. The audit never substitutes stored produced values on failure. Each successful output records matrices, inverse-bind skin products, default leaves and visited processors. Every blocked path records its exact blocking expression or message in wiiu-skin-output-coverage.json.

Five newly used outputs are hairStart, both Shoulder_Spin and both Clavicle influences. Evaluated coverage (24/64) mode replaces their carried contributions with evaluated skin matrices; earlier modes remain selectable. This can expose partial-palette seams where descendants are still carried. Maximum vertex difference from the previous face mode reaches approximately 0.0823 source mesh units; that is a movement difference, not a validation score.

The preview includes a collapsed output-coverage table for the new mode, distinguishing evaluated, carried and bind-pose influences. Counts: {'evaluated': 24, 'carried': 27, 'bind pose': 13}. Table categories describe the partial preview, not overall reverse-engineering completion.

All 20 mode/frame script checks plus focus/reset/orbit/zoom handlers pass. These are canvas-stub checks; browser visual parity remains unverified. The source-default snapshot, approximate time arithmetic and PC/Wii U numerical-equivalence limits remain in force. Production viewer unchanged.

Next decoder targets are relationship blobs beyond 34/41, translation-offset connection variants and component composition. Hair/finger dynamics remain blocked rather than guessed. No new game capture is required for this static dependency audit.

Reproduce from workspace root:
```
python WiiUResearch/AnimationViewerResearch/audit_wiiu_skin_outputs.py
python WiiUResearch/AnimationViewerResearch/build_eyelid_diagnostic.py
node WiiUResearch/AnimationViewerResearch/EyelidDiagnostic/check-preview.cjs
```
