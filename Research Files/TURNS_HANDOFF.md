> Update: the previously excluded motion is now enabled after independent native-output validation. See [NATIVE_ANKLE_VALIDATION.md](NATIVE_ANKLE_VALIDATION.md). The text below records the earlier checkpoint.

# Five source turn motions — 2026-10-22

Restart via Launch_Viewer.cmd and click **Turns**, then select a clip in the existing dropdown:

45° left/right, 90° left, and 180° left/right.

These are the extracted native **skeletal source motions**. No guessed actor yaw, world displacement or camera rotation was added. Game turn-state/actor-facing behavior remains separate. The labels are the authored clip names, not a measured assertion of final world orientation.

## Extraction and configuration

QuickBMS with the existing disney_infinity.bms extracted the wildcard *grl_bm_turn*.oct from the installed PC assets/characters/fro_elsa/fro_elsa.zip into InstalledGameAssetCheck/TurnMotions. Eight files were found: the six ordinary45/90/180turns plus two turn0landstop clips, which are not enabled here. Game assets were read only. Extraction hashes/provenance: ElsaSceneResearch/ControllerState/turn-extraction-provenance.json.

The exact Elsa BENT aliases TURN45L/R,TURN90L/R,TURN180L/R were checked by the existing source configuration reader. All six candidates' referenced ports map to this verified PC rig. Turn profiles apply passive idle phase zero as an explicit initializer for missing leaf controls, followed by the source turn clip; no invented upper-body layer is added. Full-palette graph evaluation and existing matrix/dynamics fixtures are reused. Automatic action/state selection is not reconstructed.

## Passed artifacts

NativePreviews/native-turn45l-full-palette.json, native-turn45r-full-palette.json, native-turn90l-full-palette.json, native-turn180l-full-palette.json and native-turn180r-full-palette.json all pass62/62-bone coverage and existing endpoint, native matrix, shear and dress checks.45/90clips last0.6000000238418579s (19saved samples);180clips last0.9333333373069763s (29samples).

The largest endpoint error among the accepted bakes is5.842514615749709e-6 and largest native matrix component error2.980232238769531e-7. These are numeric invariants, not game visual accuracy measurements.

build_turn_pack.py verifies hashes, TURN aliases,62-bone finite samples, increasing times, final duration and nontrivial motion before producing NativePreviews/turn-pack.json and turn-pack-validation.json. The pack records actor-yaw and initialization limits explicitly, including for the first bakes made before the extra per-artifact scope sentence was added.

## 90° right is excluded

grl_bm_turn90r fails the unchanged ankle-endpoint invariant at frame1, ankle450:1.28746575562e-5 exceeds1e-5. It is extracted but removed from enabled profiles and recorded under blocked_profiles in the catalog, so choosing that exact source hash produces a specific diagnostic. No threshold was relaxed and no successful output was generated. The cause remains unestablished; the small residual alone does not prove a visible defect. Do not redirect it to another turn or mirror a clip to fabricate success.

## Viewer and next work

The new Turns shortcut loads the five-clip pack. Launch_Viewer.cmd prefers the separate bin/TurnPreview build; older builds and packs remain. Build passes with zero warnings/errors. The --turn-pack-smoke-test loads the shortcut, checks five clips/62source bones, renders a pose from each, then runs the existing skinning checks. It does not establish game parity.

Next: user visual review of the five source turns, then inventory/extract ordinary jump, air/fall and landing references and inspect any BANM composition. Keep mounted/additive clips distinct from standalone character motions. The finger investigation remains parked per the user's request.
