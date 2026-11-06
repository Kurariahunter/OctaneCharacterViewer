# Controller source and selected-row state capture

2026-10-19

Seven native getter-chain cases pass with synthetic pointer graphs and original instructions, without call-result stubs. Source asset resolves as controller +0x78 -> handle +0x20 -> descriptor +0x10 -> wrapper +0x0C (0x76D180 -> 0x7B2500 -> 0x76C900 -> 0x6148D0). Layer configuration independently resolves from handle +0x24/+0x28 via 0x76CC50. Missing source descriptor/wrapper/asset can coexist with a valid configuration row; missing row owner can coexist with a valid source. This establishes pointer ownership/access, not active actor or time semantics.

The controller's +0x50 field is returned directly by getter 0x19368D0. Its state layout is not yet fully interpreted. Reference setup 0x7824B0 uses this object alongside source selection, configuration, and contributor registration. No numeric field is newly labeled as normalized clip time in this step.

Prepared F:/DisneyInfinityPortalTest/OctaneLiveInspector/CheatEngine/DI3_ControllerStateLogger.lua. It preserves the known working mapping capture and hardware blend-return breakpoint and adds bounded per-contribution snapshots: controller RTTI candidate, source getter chain, configuration row/index/count/names, resolved filter/mirror pointers, resolved-object RTTI/header, and raw +0x50 state bytes. Existing captures and logger files remain unchanged. F8 starts only when the scene is ready; F9 stops. Output prefix ce_controllerstate_.

The new state layout is a candidate for each observed controller until RTTI and captured contents are checked. A raw state header is not assumed to be a universal time object. Source getter tests do not prove source asset name field offsets, so the logger does not fabricate a filename from arbitrary source memory. Owner name from the earlier map capture remains a source-map hint, not actor identity.

How to run: attach Cheat Engine to the expected DisneyInfinity3.exe; remove existing debugger breakpoints; load/execute the new script in the Lua Engine; return to the fully loaded Elsa scene; press F8 and remain idle briefly, then walk/run. It stops at 120 captured blend events or 15 seconds; F9 can stop sooner. Provide the generated ce_controllerstate_*.jsonl from OctaneLiveInspector/Captures. Keep the original event limits: this is a targeted identity/state probe, not a long performance recording. It may stop before the movement transition, which is acceptable for the first identity check.

Validation: source-link-validation.json contains seven passing native cases. The Lua addition has been manually reviewed, but no Lua interpreter or live Cheat Engine run was performed for this new variant. The prior map logger has live 150/150 mapping evidence; that does not automatically validate the added state fields. No viewer motion was changed.

Next inspect captured controller RTTI and source/configuration associations, then trace only the actual encountered state type's time-update function. Once the concrete controller is identified, a longer filtered capture can isolate its timing and weights without unrelated Bullseye controllers.
