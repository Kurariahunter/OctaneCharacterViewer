"""Decode the source header parent/count layout and verify every skin association."""
import json
from pathlib import Path
from evaluate_elsa_head import T,N,DN,get,allnodes
layout=get(N,'HeaderLayout');strings=get(N,'HeaderStrings');indices=get(N,'HeaderStringIndices');parents={};cursor=1
assert len(layout)%2==0
for parent,count in zip(layout[::2],layout[1::2]):
 for child in range(cursor,cursor+count):
  assert child not in parents;parents[child]=parent
 cursor+=count
assert cursor-1==len(indices)
def path(header):
 pieces=[];seen=set()
 while header:
  if header in seen:raise ValueError('header cycle')
  seen.add(header);pieces.append(strings[indices[header-1]]);header=parents[header]
 return '|'.join(reversed(pieces))
paths={i:path(get(n,'Header')) for i,n in DN.items()};rows=[]
for association in allnodes(T,'Association'):
 if get(association,'Type')!='SkinInfluence':continue
 matches=[i for i,p in paths.items() if p==get(association,'NodeName')];assert len(matches)==1,(association,matches);rows.append({'path':get(association,'NodeName'),'node':matches[0],'influences':get(association,'InfluenceRefs')})
assert len(rows)==64
if __name__=='__main__':
 report={'scope':'HeaderLayout parent/count records assign consecutive child header IDs. All complete association paths compared exactly, without terminal-name guessing.','headers':len(indices),'parent_records':len(layout)//2,'skin_associations':rows,'dynamic_chain_position_paths':{str(i):paths[i] for i in [715,719,731,735,746,750]},'cached_rotation_resolution':{'literal':'^.Orientation','evidence':'Factory0x4aa811; data reference type filter0x4916d0; cached target read as quaternion at target+34 by helper0x49a3a0. Target paths follow sibling Transform.Orientation of particle start translation. Full original name resolver not executed.','left_rotation_node':724,'right_rotation_node':739}}
 Path('header-path-validation.json').write_text(json.dumps(report,indent=2));print('EXACT_SKIN_PATHS',len(rows))
