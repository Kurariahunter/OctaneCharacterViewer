"""Static dependency inventory from original PC rig associations; not execution coverage."""
import json,hashlib,collections
from pathlib import Path
from pc_skin_palette import *
root=R.parent/'OctaneCharacterViewer'
bake=json.loads((R/'pc-run-braid-animation.json').read_text())
reachable=set();processors={};state=[]
def visit(node,stack=()):
 if node in stack:
  state.append({'node':node,'path':PC_RIG.paths.get(node),'cycle':list(stack)+( [node])});return
 if node in reachable:return
 reachable.add(node)
 if node not in PROD:return
 p,output=PROD[node];pid=int(p['value']);typ=get(p,'Type');processors[pid]=p
 pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
 for attr,ref in pairs:
  if typ.endswith('ComponentProcessorDecompose'):
   if attr!='Aggregate':continue
  elif attr.startswith('Output')or attr.startswith('Position[')and typ=='DynamicChain' or attr=='Aggregate'and typ.endswith('ComponentProcessorCompose'):continue
  if attr.startswith('Last')or attr.startswith('Velocity['):
   state.append({'processor':pid,'attribute':attr,'node':ref,'path':PC_RIG.paths.get(ref),'kind':'persistent state input'})
  visit(ref,stack+(node,))
for name,node in skin.items():visit(node)
types=collections.Counter(get(p,'Type')for p in processors.values())
fallback=[{'bone':name,'source_output':skin[name],'path':PC_RIG.paths[skin[name]]}for name in worlds if name not in bake['source_skin_nodes']]
sourcefiles=[R/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct',Path(r'F:\Games\Disney Infinity - Gold Collection\Disney Infinity 3.0\DisneyInfinity3.exe')]
report={'scope':'Static dependency reachability for all62 PC Elsa skin influences, not proof every path is implemented or executed','sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sourcefiles], 'source_driven_bones':bake['source_skin_nodes'],'fallback_bones':fallback,'reachable_nodes':len(reachable),'processor_count':len(processors),'processor_types':dict(sorted(types.items())),'state_edges':state,'processors':[{'id':pid,'type':get(p,'Type'),'attributes':dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))}for pid,p in sorted(processors.items())]}
(root/'dependency-inventory.json').write_text(json.dumps(report,indent=2))
lines=['# Character-preview dependency inventory','',report['scope'],'',f"Current bake:46/62 source-driven palette bones. Static whole-skin closure: {len(reachable)} nodes, {len(processors)} processors, {len(types)} processor types.",'','## Remaining fallback bones','']
lines += [f"- {x['bone']}: node{x['source_output']} — `{x['path']}`"for x in fallback]
lines += ['','## Processor types in the full skin closure','','Counts below describe static reachability, not implementation status. Existing evaluator deliberately rejects unsupported paths.','', '| Processor type | Count |','|---|---:|']
lines += [f'| {typ} | {count} |'for typ,count in sorted(types.items())]
lines += ['','## Reconstructed versus substituted behavior','', '- Source identity, mapping tables, decoded tracks, mesh weights and inverse binds are file-derived.','- Curve, rotation, selected blend, relationship, IK, transform and chain routines are executed offline from the installed EXE. Native function fixtures supply object headers, cached numeric inputs and type metadata.','- The graph is evaluated by our bounded Python dispatcher, not the complete original network scheduler.','- Four source run layers/control sets are selected explicitly. Full game state-machine decisions and runtime layer composition are not reconstructed.','- Gravity, settling duration and in-place root behavior are fixture choices. Exact game contacts, forces and update order remain unresolved.','- Dress and braid feedback conventions are reconstructed; braid needs a synchronized live-game reference.','- Manual finger adjustments remain separate preview diagnostics and are absent from standalone raw playback.','', '## Next live-game capture request','', 'No new broad Cheat Engine scan is needed to open this prototype. Before requesting captures, map these fields to stable verified addresses and identify the player actor:','', '1. Active clip identifiers, local times, weights, blend modes and control values for one steady run.','2. Final62 skin palettes plus frame/timestamp and actor identity.','3. Chain548 input anchor/container/constraint, force, previous local orientation, output positions and type tags in the same frames.','4. A short idle-to-run transition and a steady run segment.','', 'Do not treat an arbitrary controller event as Elsa without actor identity. Existing captures and logger limits remain relevant. Only read/copy data for this research; no gameplay values need to be patched.','', '## Completion milestones','', '1. Independent viewer with original mesh and native-evaluated cached poses (this prototype).','2. Backend input/output contract, cancellation, diagnostics and generic clip selection within validated formats.','3. Match recorded game palettes at known clip times and layer state.','4. Remove fixture dependencies incrementally; support another complete clip and another character.','5. Only then investigate direct original loader/scheduler execution with correct object constructors, allocation, type registration and external-service stubs.','', 'A complete game engine is outside this milestone. Rendering uses WPF, not the original engine renderer. Raw binary asset import still uses a one-time Unity mesh export bridge; normal viewer playback and evaluator refresh do not require Unity.']
(root/'DEPENDENCY_INVENTORY.md').write_text('\n'.join(lines),encoding='utf-8')
print('Inventory saved:',len(reachable),'nodes',len(processors),'processors',len(types),'types')
