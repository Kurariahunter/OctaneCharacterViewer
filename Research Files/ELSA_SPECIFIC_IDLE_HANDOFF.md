# Elsa-specific idle checkpoint — 2026-10-20

Rebaked the pinned original-PC `elsa_bm_idle_active.oct` with the current decoder. This is a previously supported character-specific profile, freshly validated rather than a new unsupported motion family. Startup bundle now contains the three runs plus `elsa_bm_idle_active_NativePreview`.

253 simulation frames / 127 samples / 4.2 seconds. Bake passes: endpoint error 5.73e-7, native matrix error 2.68e-7, shear 1.39e-7. WPF selected-clip smoke passes, with nonzero mesh displacement 0.0635. Independent skinning checks pass on three poses / 5419 vertices, error 4.44e-16. Screenshot inspected. Existing fixture dynamics, fallback bones and unresolved index issue remain; this is not full game visual parity.

User-supplied clean Yoda ZIP inventoried read-only: 933 entries, none marked ZIP-encrypted. SHA and member list are saved in yoda-clean-source-inventory.json. This establishes provenance for the next rig extraction, not Yoda animation support. No old downloaded Yoda model was reused.

Reopen Launch_Viewer.cmd and select elsa_bm_idle_active_NativePreview. Existing runs remain available. Next: independently extract and inspect the clean Yoda skeleton and motion bindings; avoid assuming Elsa controller indices.
