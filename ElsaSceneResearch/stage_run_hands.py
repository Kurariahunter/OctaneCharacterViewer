from pathlib import Path
import shutil,json
p=Path(r'F:\DisneyInfinityPortalTest\ElsaSceneResearch')
a=json.loads((p/'pc-run-lean-animation.json').read_text());b=json.loads((p/'pc-run-hands-animation.json').read_text())
base=set(a['source_skin_nodes']);maximum=0
for x,y in zip(a['clips'][0]['samples'],b['clips'][0]['samples']):
 old={t['bone']:t['matrix']for t in x['transforms']};new={t['bone']:t['matrix']for t in y['transforms']}
 maximum=max(maximum,max(abs(v-w)for n in base for v,w in zip(old[n],new[n])))
if maximum>1e-8:raise ValueError(('body regression',maximum))
(p/'pc-run-hands-regression.json').write_text(json.dumps({'unchanged_previous_source_bones':len(base),'max_matrix_difference':maximum,'new_source_bones':sorted(set(b['source_skin_nodes'])-base)},indent=2))
for root in [Path(r'C:\Users\Kurar\Disney Reloaded'),Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation')]:
 editor=root/'Assets/DI3PCRunHandsPreview/Editor';(editor/'Data').mkdir(exist_ok=True)
 shutil.copy2(p/'pc-run-hands-animation.json',editor/'Data/pc-run-hands-animation.json')
 code=(editor/'DI3PCRunHandsPreview.cs').read_text();start=code.index('  File.WriteAllText(Output+"/README.txt",');end=code.index('AssetDatabase.SaveAssets();',start)
 code=code[:start]+'  File.WriteAllText(Output+"/README.txt","PC run hands comparison. Left: previous run plus lean. Right: native finger relationship outputs and source hairStart added. Dynamic hair01 and hair02 remain bind-relative fallback. Body and dress source matrices unchanged. Manual game visual validation pending.\\n"+string.Join("\\n",report));'+code[end:]
 (editor/'DI3PCRunHandsPreview.cs').write_text(code)
print('Previous 31 source bone matrices unchanged:',maximum)
