"""Decode the existing bounded static command layout using source-template ports."""
import base64,struct,copy
from wiiu_port_records import read_records
from source_asset_tree import parse

def static_frame(oct_path,tree_path,endian='>'):
 raw=base64.b64decode(next(n['value']['base64']for n in parse(oct_path)['nodes']if n['key']=='ClipDataBlock'));assert struct.unpack_from(endian+'IIHH',raw)==(0,0,1,0)
 path=oct_path.with_suffix('.oct.clipdata');path.write_bytes(raw);records=read_records(path,tree_path,endian=endian);assert all(r['phase']=='static'for r in records)
 ports={}
 for row in records:
  if row['source_node']is None:continue
  target=ports.setdefault(str(row['port']),{'source_node':row['source_node'],'path':row['path'],'channels':{}})
  for d in row['descriptors']:target['channels'][str(int(d['opcode'],16))]={'values':list(d['values'])}
 return {'time':0.,'ports':ports}

def initialized(base,frame):
 result=copy.deepcopy(base);result['time']=frame['time']
 for p,row in frame['ports'].items():
  if p not in result['ports']:result['ports'][p]=copy.deepcopy(row)
  else:result['ports'][p]['channels'].update(copy.deepcopy(row['channels']))
 return result
