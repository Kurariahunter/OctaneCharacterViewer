"""Compare bounded finger hierarchy matrix operations with original native math."""
from pc_skin_palette import PROD,DN,get,skin
from evaluate_pc_raw_transform import dilation
from native_pc_dress_math import call
from evaluate_pc_arms import quat
import numpy as np

SPECS={'ConcatenateChainDilation':0x4D1CB0,'ConcatenateChainInverseDilation':0x4D2B00,'InvertDilation':0x4D19C0}
def audit(e):
    stops={skin[n]for n in ('Hand_Left','Hand_Right')}
    visited=set();checks=[];other=[]
    def visit(node):
        if node in visited or node in stops:return
        visited.add(node);producer=PROD.get(node)
        if not producer:return
        p,attr=producer;typ=get(p,'Type')
        if typ=='RelationshipProcessor':return
        pairs=list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')))
        refs=[v for a,v in pairs if v!=node and not a.startswith('Output')]
        for v in refs:visit(v)
        if typ in SPECS and 1<=len(refs)<=8:
            normal_count=sum(a.startswith('Input[') for a,v in pairs) if typ=='ConcatenateChainInverseDilation' else None
            raw=call(SPECS[typ],[dilation(e.run(v))for v in refs],'array',8,normal_input_count=normal_count)
            m=np.eye(4);m[:3,:3]=quat(raw[:4])*raw[7];m[:3,3]=raw[4:7]
            error=float(np.max(abs(m-e.run(node))))
            if error>1e-5:raise ValueError('Finger hierarchy native mismatch at '+str(node))
            checks.append({'node':node,'processor':int(p['value']),'type':typ,'max_matrix_error':error})
        else:other.append({'node':node,'type':typ,'scope':'Not compared by this bounded hierarchy audit'})
    for name,node in skin.items():
        if any(s in name for s in ('Thumb','Index','Middle')):visit(node)
    return {'checks':checks,'other_nodes':other,'scope':'One-to-eight input chain Dilation and unary inversion operators only; stops at hands and relationship outputs. Supplied evaluator inputs; not independent full-graph/game validation.'}
