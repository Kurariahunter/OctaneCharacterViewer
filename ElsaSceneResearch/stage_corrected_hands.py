from pathlib import Path
import shutil,json
r=Path(r'F:\DisneyInfinityPortalTest\ElsaSceneResearch');prod=Path(r'C:\Users\Kurar\Disney Reloaded');v=Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation')
old=json.loads((r/'pc-run-lean-animation.json').read_text());new=json.loads((r/'pc-run-hands-corrected-animation.json').read_text());base=set(old['source_skin_nodes']);error=0
for a,b in zip(old['clips'][0]['samples'],new['clips'][0]['samples']):
 x={p['bone']:p['matrix']for p in a['transforms']};y={p['bone']:p['matrix']for p in b['transforms']};error=max(error,max(abs(v-w)for n in base for v,w in zip(x[n],y[n])))
assert error==0
source=(prod/'Assets/DI3PCRunHandsPreview/Editor/DI3PCRunHandsPreview.cs').read_text().replace('DI3PCRunHandsPreview','DI3PCRunHandsCorrectedPreview').replace('PC_RunHands','PC_RunHandsCorrected').replace('Run Hands','Run Hands Corrected').replace('pc-run-hands-animation','pc-run-hands-corrected-animation')
source=source.replace('Right: native finger relationship outputs and source hairStart added.','Right: native finger outputs with authored joint positions preserved; coherent braid fallback chain.').replace('Left: previous run plus lean.','Left: previous run plus lean (open fallback hands).')
for root in [prod,v]:
 p=root/'Assets/DI3PCRunHandsCorrectedPreview/Editor';(p/'Data').mkdir(parents=True,exist_ok=True)
 (p/'DI3PCRunHandsCorrectedPreview.cs').write_text(source);shutil.copy2(r/'pc-run-hands-corrected-animation.json',p/'Data/pc-run-hands-corrected-animation.json')
print('Body/dress regression maximum:',error)
