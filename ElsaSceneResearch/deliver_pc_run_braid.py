from pathlib import Path
import json,shutil
r=Path(r'F:\DisneyInfinityPortalTest\ElsaSceneResearch');prod=Path(r'C:\Users\Kurar\Disney Reloaded');v=Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation\Assets\DI3PCRunBraidPreview')
p=prod/'Assets/DI3PCRunBraidPreview';shutil.copytree(v/'Generated',p/'Generated',dirs_exist_ok=True);shutil.copy2(v/'Generated.meta',p/'Generated.meta')
notes='''# PC Elsa native braid checkpoint

Open Assets/DI3PCRunBraidPreview/Generated/Elsa_PC_RunBraid_Preview.unity and press Play.
Left: previous continuous bind-relative fallback braid. Right: native source braid simulation. Mouse rotation and braid/head close-up apply automatically. The comparison uses identical raw source hand poses; saved visual hand calibration is recorded separately and is not decoder evidence.

## Source path

Verified installed PC Elsa OCT and executable identities remain unchanged. Braid processor 548 is DynamicChain, separate from dress 550/551. The reset fixture now accepts an explicit Hair selection, selecting 548's own ChainData and both particle binds. The chronological state adapter accepts this exact additional processor; it still rejects unknown IDs and invalid time steps. Braid particles both use Dilation binds, damping factor 1.5, natural frequency 12.566370964, drag 0.5, and distal constraint length 0.179999992. Container extent is [0.1,0.07,0.15073344]. No dress constants are substituted.

Constraint processor 549 evaluates node862 by original native Transform point conversion using local point861 and root Transform471. Native chain reset/full/step entry points are 0x4acad0 / 0x4ae360 / 0x4acdb0. Root positions678/683 drive local translation677/682. Local Aim671 uses inverse-transformed segment direction676 and authored align/up references; its previous local quaternion is fed back to chain548 using the established fixture mechanism. This feedback setup is an offline reconstruction, not a live-captured braid parity claim. Outputs hair01/681 and hair02/686 now replace fallback.

## Validation

32-frame native fixture: exact repeatability and exact full-dispatch versus staged-dispatch equality; root error zero; maximum segment-length error 2.75e-7. Three malformed processor/time cases rejected. Run bake: 120 settling ticks, 60 Hz simulation, 73 exported poses at30 Hz over four 0.6-second cycles. Source-driven palette increased44 to46 of62. Previous44 source-driven bone matrices match exactly, including body, hands, dress and hairStart. Endpoint maximum error1.17e-6. Run chain root error0; segment-length maximum2.02e-7. Unity build and six rendered sample checks passed. Side-view rendered poses0.1s and1.2s visually inspected: right braid bends downward relative to left, without the prior disconnected fallback shape.

## Limits and next step

This is a file/native-code-based braid reconstruction baked into Unity animation, not a new runtime Unity physics simulation and not proven original-game equivalence. Gravity uses the existing fixture force [0,-9.81000042,0]. Exact game forces, contacts/capsules, update ordering, root locomotion and braid orientation feedback must still be compared. In-place run has no moving-world acceleration. No seamless loop claim; playback is one-shot over2.4s. Facial animation, remaining16 palette fallbacks, thumb pose and full source layer composition remain unresolved.

Next review the right braid during playback against the original game run. Once this structural check is acceptable, validate another complete source clip before broadening the reader to another character; do not infer generic character support from the Elsa-specific evaluator.

## Hand calibration checkpoint

hand-visual-comparison-checkpoint.json records screenshot120342: tip weight1, proximal0 degrees, gap1.34, tip bend0, side-20, twist-17. Thumb unresolved. These are user visual offsets only; no source decoding correction inferred.
'''
(r/'PC_NATIVE_BRAID_HANDOFF.md').write_text(notes,encoding='utf-8')
d=prod/'Tools/ExecutableResearch/DressResearch'
for name in ['PC_NATIVE_BRAID_HANDOFF.md','hand-visual-comparison-checkpoint.json','pc-braid-native-validation.json','pc-run-braid-regression.json','pc-run-braid-validation.json','native_pc_chain_reset.py','native_pc_chain_step.py','evaluate_pc_braid.py','validate_pc_braid_native.py','bake_pc_run_braid.py']:
 shutil.copy2(r/name,d/name)
master=prod/'Tools/ExecutableResearch/DISNEY_INFINITY_3_EXE_RESEARCH.md'
with master.open('a',encoding='utf-8')as f:f.write('\n\n## 2026-10-18: PC braid548 offline native reconstruction\n\nSee DressResearch/PC_NATIVE_BRAID_HANDOFF.md. Braid own source chain/particle data, native frame stepping and local Aim feedback now supply hair01/hair02. Previous44 source bone matrices unchanged;46/62 now source-driven. Native invariants and Unity build/render pass; exact live braid parity remains unverified. Visual hand offsets are separately checkpointed and not decoder evidence.\n')
print(p/'Generated/Elsa_PC_RunBraid_Preview.unity')
