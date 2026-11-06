from pathlib import Path
import json,shutil
r=Path(r'F:\DisneyInfinityPortalTest\ElsaSceneResearch');prod=Path(r'C:\Users\Kurar\Disney Reloaded');v=Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation')
old=json.loads((r/'pc-run-hands-corrected-animation.json').read_text());new=json.loads((r/'pc-run-braid-animation.json').read_text());base=set(old['source_skin_nodes']);error=0;hairchange=0
for a,b in zip(old['clips'][0]['samples'],new['clips'][0]['samples']):
 x={p['bone']:p['matrix']for p in a['transforms']};y={p['bone']:p['matrix']for p in b['transforms']};error=max(error,max(abs(v-w)for n in base for v,w in zip(x[n],y[n])));hairchange=max(hairchange,max(abs(v-w)for n in ['hair01','hair02']for v,w in zip(x[n],y[n])))
assert error==0 and hairchange>1e-5
(r/'pc-run-braid-regression.json').write_text(json.dumps({'unchanged_source_bones':len(base),'max_matrix_difference':error,'braid_changed_max_matrix_difference':hairchange},indent=2))
source=(prod/'Assets/DI3PCRunHandsCorrectedPreview/Editor/DI3PCRunHandsCorrectedPreview.cs').read_text().replace('DI3PCRunHandsCorrectedPreview','DI3PCRunBraidPreview').replace('PC_RunHandsCorrected','PC_RunBraid').replace('Run Hands Corrected','Run Braid').replace('pc-run-hands-corrected-animation','pc-run-braid-animation')
source=source.replace('Assets/DI3PCRunLeanPreview/Generated/grl_bm_runf_PC_RunLean.prefab','Assets/DI3PCRunHandsCorrectedPreview/Generated/grl_bm_runf_PC_RunHandsCorrected.prefab')
a=source.index('  File.WriteAllText(Output+"/README.txt",');b=source.index('AssetDatabase.SaveAssets();',a)
source=source[:a]+'  File.WriteAllText(Output+"/README.txt","PC braid comparison. Left: continuous bind-relative braid fallback. Right: native braid548 simulation, own source particles and container, root constraint and local Aim feedback. Identical raw source hand poses; visual hand offsets remain separate diagnostics. 46 source-driven palette bones; remaining 16 fallback. Full game force, collision, timing and braid feedback parity remain unverified.\\n"+string.Join("\\n",report));'+source[b:]
for root in [prod,v]:
 p=root/'Assets/DI3PCRunBraidPreview/Editor';(p/'Data').mkdir(parents=True,exist_ok=True);(p/'DI3PCRunBraidPreview.cs').write_text(source,encoding='utf-8');shutil.copy2(r/'pc-run-braid-animation.json',p/'Data/pc-run-braid-animation.json')
preset={'scope':'User visual comparison preset only; not verified native decoding','reference':'Screenshot 2026-10-18 120342.png','source_tip_weight':1,'index_knuckle_degrees':0,'gap_closure':1.34,'tip_bend_degrees':0,'tip_side_degrees':-20,'tip_twist_degrees':-17,'thumb':'unresolved'}
(r/'hand-visual-comparison-checkpoint.json').write_text(json.dumps(preset,indent=2))
print('Unchanged prior source matrices:',error,'braid difference:',hairchange)
