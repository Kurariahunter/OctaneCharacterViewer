from pathlib import Path
import json,struct,base64,collections
p=Path('WiiUResearch/AnimationViewerResearch');tree=json.loads((p/'WiiUClips/fro_elsa.tree.json').read_text())
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k):return next((c['value']for c in n['children']if c['name']==k),None)
net=next(n for n in walk(tree)if n['name']=='SubNetwork');nodes={int(n['value']):n for n in walk(net)if n['name']=='DataNode'};link=next(n for n in walk(net)if n['name']=='BaseDataNodeLinks')
def shorts(x):
 b=base64.b64decode(x);return struct.unpack('>'+str(len(b)//2)+'H',b)
used=get(net,'ConnectionMapUsedDataNodes');localused=shorts(get(link,'LocalUsedDataNodeIndices'));ports=shorts(get(link,'LocalToPortIndices'));reverse=shorts(get(link,'PortToLocalIndices'))
assert len(localused)==len(ports)==len(used);assert sorted(localused)==list(range(len(used)))
lookup={}
for local,(slot,port)in enumerate(zip(localused,ports)):
 assert reverse[port]==local
 lookup[port]=used[slot]
print('source ports',len(lookup),'reverse extent',len(reverse),'sentinel',sum(x==65535 for x in reverse))
# Header paths are source names, not guessed retail bone names.
layout=get(net,'HeaderLayout');indices=get(net,'HeaderStringIndices');strings=get(net,'HeaderStrings');parents={};cursor=1
for parent,count in zip(layout[::2],layout[1::2]):
 for i in range(cursor,cursor+count):parents[i]=parent
 cursor+=count
assert cursor-1==len(indices)
paths={}
for i,n in nodes.items():
 h=get(n,'Header');path=[];seen=set()
 while h:
  assert h not in seen;seen.add(h);path.append(strings[indices[h-1]]);h=parents[h]
 paths[i]='|'.join(reversed(path))
b=(p/'WiiUClips/elsa_bm_idle_specific01.oct.clipdata').read_bytes();U=lambda fmt,at:struct.unpack_from('>'+fmt,b,at)
regs,ncurves=U('HH',U('I',16)[0]);start=U('I',16)[0];curvefirst=U('I',20)[0];pool=U('I',12)[0];pos=start+4+ncurves*2;size,count=U('HH',pos);pos+=4;codes=U('H'*count,pos);pos+=count*2;records=[]
for phase,words in [('timed',codes)]:
 for code in words:
  n,port=code>>13,code&8191;assert 1<=n<=7;descriptors=[]
  for _ in range(n):
   op=U('H',pos)[0];group=op&0xf000;width=4 if group==0 else 8 if group in(0x1000,0x2000,0x3000)else None;assert width
   fields=U('H'*(width//2),pos);pos+=width
   if group==0:
    assert op in (0x11,0x12,0x13,0x16,0x17,0x18,0x1a) and fields[1]<regs
   elif group==0x1000:
    for ref,shift in zip(fields[1:],(4,2,0)):
     mode=(op>>shift)&3;assert mode in (0,1)
     assert ref<(regs if mode==1 else (len(b)-pool)//4)
   else:raise ValueError('Descriptor class not validated in source sample')
   descriptors.append({'opcode':hex(op),'fields':fields})
  records.append({'phase':phase,'port':port,'source_node':lookup.get(port),'path':paths.get(lookup.get(port)),'descriptors':descriptors})
assert pos==start+size,(pos,start+size)
staticcount=U('H',pos)[0];pos+=2;codes=U('H'*staticcount,pos);pos+=staticcount*2
for code in codes:
 n,port=code>>13,code&8191;assert 1<=n<=7;descriptors=[]
 for _ in range(n):
  op,index=U('HH',pos);pos+=4;width={0:3,1:1,2:1,3:1,4:4,5:3,10:1}.get(op);assert width and index+width<=(len(b)-pool)//4
  descriptors.append({'opcode':hex(op),'pool_index':index,'values':U('f'*width,pool+index*4)})
 records.append({'phase':'static','port':port,'source_node':lookup.get(port),'path':paths.get(lookup.get(port)),'descriptors':descriptors})
assert (pos+3)&~3==curvefirst,(pos,curvefirst)
print('commands',collections.Counter(r['phase']for r in records),'unmapped',[(r['phase'],r['port'])for r in records if r['source_node']is None]);print('dynamicopcodes',collections.Counter(d['opcode']for r in records if r['phase']=='timed'for d in r['descriptors']))
for r in records[:8]:print(r['port'],r['source_node'],r['path'])
(p/'elsa-output-port-map.json').write_text(json.dumps({'connection_template':get(link,'ConnectionTemplate'),'source_ports':len(lookup),'reverse_extent':len(reverse),'records':records},indent=2))

for record in records:
 if record['source_node']is None:assert record['port']<len(reverse)and reverse[record['port']]==65535
from inspect_wiiu_clip import inspect
clip_range=U('ff',0);report=inspect(b,[clip_range[0],sum(clip_range)/2,clip_range[1]])
assert U('H'*ncurves,start+4)==tuple(range(ncurves))
samples=[]
for frame in range(3):
 registers=[v for curve in report['curves']for v in curve['samples'][frame]['values']];assert len(registers)==regs
 channels={}
 for phase in ['static','timed']:
  for record in records:
   if record['phase']!=phase or record['source_node']is None:continue
   node=channels.setdefault(str(record['port']),{'source_node':record['source_node'],'path':record['path'],'channels':{}})
   for desc in record['descriptors']:
    op=int(desc['opcode'],16)
    if phase=='static':node['channels'][str(op)]={'kind':'constant','values':desc['values']}
    elif op&0xf000==0x1000:
     fields=desc['fields'];vals=[]
     for ref,shift in zip(fields[1:],(4,2,0)):
      vals.append(registers[ref]if (op>>shift)&3==1 else U('f',pool+ref*4)[0])
     node['channels']['4']={'kind':'raw Euler operands; rotor conversion pending','order_code':(op>>6)&7,'values':vals}
    else:node['channels'][str(op-16)]={'kind':'evaluated scalar','values':[registers[desc['fields'][1]]]}
 samples.append({'time':report['curves'][0]['samples'][frame]['time'],'ports':channels})
(p/'elsa-raw-control-samples.json').write_text(json.dumps({'scope':'Three raw file-derived control samples; no native execution, rotor conversion, graph evaluation or final palette. Cubic timing follows inspector assumptions, not proven exact native time quantization. Out-of-domain flags0 uses native-confirmed start/end holds; no other boundary modes admitted.','samples':samples},indent=2))
print('PASS operand bounds, exact command extents, 2 explicit unmapped sentinels; wrote3raw control samples')
