from pc_skin_palette import *
from native_pc_relationship import run
rows=[]
for pid in [165,171,173,175]:
 p=next(p for p in allnodes(N,'ProcessorNode')if int(p['value'])==pid);pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')));refs=dict(pairs);data=get(DN[refs['RelationshipData']],'RelationshipDataBlock');blob=bytes(data)if isinstance(data,list)else bytes.fromhex(data['hex']);outputs=[n for a,n in pairs if a.startswith('Output[')];initial=[]
 for n in outputs:
  f={c['name']:c['value']for c in next(c for c in DN[n]['children']if c['name']=='Data')['children']};initial.append(f.get('Orientation',[0,0,0,1])+f.get('Translation',[0,0,0])+[f.get('Scale',1.)])
 raw=run(blob,[-46.9 if 'Spread'not in PC_RIG.paths[n]else 0 for a,n in pairs if a.startswith('Input[')],len(outputs),initial)
 error=max(abs(v-w)for a,b in zip(initial,raw)for v,w in zip(a[4:],b[4:]))
 if error>1e-7:raise ValueError(('unexpected translation write',pid,error))
 rows.append({'processor':pid,'max_unchanged_translation_scale_error':error,'initial_translations':[x[4:7]for x in initial]})
(R/'pc-finger-output-initialization-validation.json').write_text(json.dumps(rows,indent=2));print('PASS: native finger relationships preserve authored translations and scale')
