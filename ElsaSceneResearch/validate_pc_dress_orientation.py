"""PC source-guided particle-position to local dress rotor validation.

Captured particle positions are inputs, not regenerated dynamics.
"""
import json,math
from pathlib import Path
from evaluate_pc_thigh_graph import procs,dn,get,child
from native_pc_dress_math import aim,inverse_vector,difference,sha
R=Path(__file__).parent
P=R.parent/'OctaneLiveInspector/Captures/octane_20261017_151848_1792264728047355700.json'
def refs(p):return dict(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
def angle(a,b):
 norms=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b));dot=abs(sum(x*y for x,y in zip(a,b)))/norms
 return math.degrees(2*math.acos(min(1,dot)))
def main():
 d=json.loads(P.read_text());anchors=json.loads((R/'pc-dress-anchor-validation.json').read_text());rows=[];mappings=[]
 for chain,source in [('0x1e07fdd0',550),('0x1e07fe74',551)]:
  dynamic=next(p for p in procs if int(p['value'])==source);dr=refs(dynamic);source_anchor=dr['AnchorToWorld']
  inverse=next(p for p in procs if get(p,'Type')=='InverseTransformVectorWithTransform' and refs(p)['Converter']==source_anchor)
  ir=refs(inverse);aimproc=next(p for p in procs if get(p,'Type')=='AimConstraintProcessorNode' and refs(p)['AlignInput']==ir['Output']);ar=refs(aimproc)
  # Require the full source difference -> inverse vector -> Aim relationship.
  diff=next(p for p in procs if get(p,'Type')=='Position3dDifferenceProcessor' and refs(p)['Output']==ir['Input']);fr=refs(diff)
  assert fr['To']==dr['Position[1]'] and fr['From']==dr['Position[0]']
  constants=[get(dn[ar[k]],'Data') for k in ['AlignReference','UpInput','UpReference']];assert all(isinstance(v,list) and len(v)==3 for v in constants)
  mappings.append({'chain':chain,'source_dynamic':source,'source_anchor':source_anchor,'source_inverse':int(inverse['value']),'source_aim':int(aimproc['value']),'source_rotor':ar['Output'],'reference_vectors':constants})
  for index,s in enumerate(d['samples']):
   c=next(c for c in s['chains'] if c['address']==chain);delta=difference(c['output_positions'][1],c['output_positions'][0]);q=c['cached_orientation']['quaternion'];anchor=c['anchor_raw16'];local=inverse_vector(delta,anchor);expected=aim(local,*constants,initial=q)
   composed=next(a['predicted_transform_raw16'] for a in anchors['rows'] if a['sample']==index and a['chain']==chain);q2=aim(inverse_vector(delta,composed),*constants,initial=q)
   rows.append({'sample':index,'chain':chain,'source_rotor':ar['Output'],'native_local_quaternion':expected,'captured_local_quaternion':q,'captured_anchor_error_degrees':angle(expected,q),'recomposed_anchor_error_degrees':angle(q2,q),'frame_lag':c['frame_raw']-c['last_frame_raw']})
 summary={chain:{'samples':sum(r['chain']==chain for r in rows),'max_captured_anchor_error_degrees':max(r['captured_anchor_error_degrees'] for r in rows if r['chain']==chain),'max_recomposed_anchor_error_degrees':max(r['recomposed_anchor_error_degrees'] for r in rows if r['chain']==chain)} for chain in [m['chain'] for m in mappings]}
 report={'capture':str(P),'exe_sha256':sha,'scope':'PC source graph constants and connectivity verified. Original native difference/inverse/Aim applied to captured particle positions, with captured and partially recomposed anchor alternatives. No temporal particle simulation, original clip decode, or Unity conversion. Captures non-atomic.','mappings':mappings,'summary':summary,'rows':rows};(R/'pc-dress-orientation-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'mappings':mappings,'summary':summary},indent=2));assert len(rows)==120
 assert max(r['captured_anchor_error_degrees'] for r in rows)<0.00001
if __name__=='__main__':main()
