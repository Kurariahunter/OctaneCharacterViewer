"""File-derived PC skin-world palette; native leg compensation and reset-only dress."""
import json,re
from pathlib import Path
from evaluate_pc_temporal_dress import *
from native_pc_chain_step import ChainStates
from evaluate_pc_raw_transform import affine
from native_pc_transform_scale import point
from read_pc_idle_files import Clip
from pc_graph_controls import apply

R=ROOT;reflect=np.diag([-1,1,1,1]);influences={int(x['value']):x for x in allnodes(T,'Influence')}
worlds={get(x,'Name'):np.linalg.inv(np.array(get(x,'BindPoseSkinLocalToWorldMatrixInverseData')).reshape(4,4).T)for x in influences.values()}
prefab=Path('C:/Users/Kurar/Disney Reloaded/Assets/DI3Converted/fro_elsa/fro_elsa_Rigged.prefab').read_text()
objects={};transforms={}
for kind,ident,body in re.findall(r'--- !u!(\d+) &(\d+)\n(.*?)(?=--- !u!|\Z)',prefab,re.S):
 if kind=='1':objects[int(ident)]=re.search(r'^  m_Name: (.*)$',body,re.M)[1]
 if kind=='4':transforms[int(ident)]={'object':int(re.search(r'm_GameObject: \{fileID: (\d+)\}',body)[1]),'parent':int(re.search(r'm_Father: \{fileID: (\d+)\}',body)[1])}
parents={objects[t['object']]:objects[transforms[t['parent']]['object']] if t['parent']in transforms else None for t in transforms.values() if objects[t['object']]in worlds}
parents={name:(parent if parent in worlds else None)for name,parent in parents.items()}
for side in ['Left','Right']:
 parents.update({'Shoulder_OL_'+side:'Shoulder_Spin_'+side,'Elbow_OL_'+side:'Shoulder_'+side,'Thumb2_'+side:'Thumb1_'+side,'Forearm_OL_'+side:'Elbow_'+side})
for name in ['LowerLidLeft','LowerLidRight','UpperLidLeft','UpperLidRight','hair02']:parents[name]='Head'
assert set(parents)==set(worlds)
names=['Body','Spine1','Spine2','Spine3','Clavicle_Left','Clavicle_Right','Shoulder_Spin_Left','Shoulder_Spin_Right','Neck','Head','Shoulder_Left','Shoulder_Right','Elbow_Left','Elbow_Right','Hand_Left','Hand_Right','Shoulder_OL_Left','Shoulder_OL_Right','Elbow_OL_Left','Elbow_OL_Right','Hips','Knee_Right','Ball_Right','Toes_Right','Knee_Left','Ball_Left','Toes_Left','UpperDress_Left','UpperDress_Right','dressLeftStart','dressRightStart']
skin={}
for a in allnodes(T,'Association'):
 if get(a,'Type')!='SkinInfluence':continue
 ids=[i for i,path in PC_RIG.paths.items()if path==get(a,'NodeName')]
 if len(ids)!=1:raise ValueError('ambiguous skin association')
 prod,attr=PROD[ids[0]]
 if get(prod,'Type')not in ('TransformToMatrix4x4VariantProcessor','DilationToMatrix4x4VariantProcessor'):raise ValueError('unrecognized skin matrix producer')
 node=dict(zip(get(prod,'DataNodeAttributes'),get(prod,'DataNodeRefs')))['Input']
 for ref in get(a,'InfluenceRefs'):skin[get(influences[ref],'Name')]=node
assert set(skin)==set(worlds)
bindlocals={name:np.linalg.inv(worlds[parent])@worlds[name] if parent else worlds[name] for name,parent in parents.items()}
