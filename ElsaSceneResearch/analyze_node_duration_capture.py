"""Full source/argument links plus native pre-selection parameter replay."""
import argparse,json,struct
from pathlib import Path
from analyze_duration_origin_capture import analyze as analyze_origin
from native_node_duration import select

def address(value):
 return int(value,16) if isinstance(value,str) else int(value or 0)
def analyze(path):
 result=analyze_origin(path);rows=[json.loads(l)for l in Path(path).read_text().splitlines()];requests={r['sequence']:r for r in rows if r['event']=='request'};checked=[];boundaries=[]
 for chain in result['chains']:
  request=requests[chain['request_sequence']]
  try:
   selection=request['selection'];assert request['selection_link']=='verified_object_owner_stack','Unverified selection link'
   assert selection['order']<request['order']and address(selection['stack'])==address(request['stack'])+20,'Selection/request frame differs'
   assert selection['owner']==request['owner']and selection['controller']==request['identity']['controller'],'Selection owner/controller differs'
   parameter=struct.unpack('<f',bytes.fromhex(selection['cached_parameter_hex4']))[0]
   payload=bytes.fromhex(selection['parameter_hex80'])
   assert payload[0x14:0x18]==bytes.fromhex(selection['cached_parameter_hex4']),'Parameter block/getter differs'
   identifier=struct.unpack_from('<I',payload)[0];assert identifier==int(chain['requested_identifier_hex'],16),'Parameter/request identifier differs'
   override=None
   if address(selection.get('override')):override=struct.unpack_from('<f',bytes.fromhex(selection['override_hex20']),8)[0]
   flags=selection['runtime_flags'];native=select(parameter,override,flags)
   assert struct.pack('<f',native)==bytes.fromhex(request['arguments_hex16'])[12:16],'Native selected duration differs'
   checked.append(dict(chain,parameter_data_address=selection['parameter_data'],configured_parameter=parameter,override=override,runtime_flags=flags,force_zero=bool(flags&4),native_selected_duration=native,selection_exact=True))
  except (AssertionError,KeyError,ValueError,TypeError,struct.error)as exc:boundaries.append(dict(request_sequence=request['sequence'],reason=str(exc)))
 result.update(node_selection_verified_chains=len(checked),node_selection_chains=checked,node_selection_boundaries=boundaries)
 result['scope']+=' Node selection uses original1448B61..1448C15 with captured cached parameter, override and flags. Live parameter block is not automatically a file-offset mapping.'
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--output',required=True);a=p.parse_args();r=analyze(a.capture);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r))
