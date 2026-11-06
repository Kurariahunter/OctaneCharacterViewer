from pc_skin_palette import *
from evaluate_pc_feedback_dress import FeedbackDressEval
from native_pc_chain_step import ChainStates
from pc_graph_controls import apply
c=Clip(next((R/'InstalledGameAssetCheck/RunMotions').rglob('grl_bm_run_upbody_add.oct')),PC_RIG)
e=FeedbackDressEval(ChainStates(force=[0,-9.8100004196167,0],strict_types=True),0,1/60);apply(e,c.sample(0))
for name in worlds:
 if any(s in name.lower() for s in ['hair','thumb','index','middle']):
  try:
   node=skin[name];v=e.raw.run(node) if get(DN[node],'Type')=='Transform' else e.run(node);print(name,'OK')
  except Exception as ex:print(name,str(ex))
for p in allnodes(N,'ProcessorNode'):
 refs=get(p,'DataNodeRefs',[])
 if any(i in refs for i in [176,201,204,207,210,213,216,219,225,231,683]):print(json.dumps(p))
