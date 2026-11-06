"""Read-only active hand contributor -> ClipProcessor -> full source hash/time observations."""
import sys,json,struct,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'OctaneLiveInspector/ReadOnlyBridge'))
sys.path.insert(0,str(ROOT/'ElsaSceneResearch'))
from client import submit
from read_pc_idle_files import tuple_decode
known={}
for path in (ROOT/'ElsaSceneResearch/InstalledGameAssetCheck/IdleMotions').rglob('*.oct'):
 v=next(r['value'] for r in tuple_decode(path.read_bytes())['records'] if r['name']=='ClipDataBlock')
 b=bytes.fromhex(v['hex']) if isinstance(v,dict) else bytes(v)
 known[b[:128]]=(path.name,b)
status=json.loads((ROOT/'OctaneLiveInspector/ReadOnlyBridge/status.json').read_text())
assert status['active'] and status['pid']==95092,'This discovery belongs to PID95092; relocate after restart'
links=json.loads((ROOT/'ElsaSceneResearch/ControllerState/idle-new-session-controller-links.json').read_text())['rows']
node=int(links[0]['inputs'][0]['node'],16)
def read(a,n):
 r=submit('READ',a,n);assert r['ok'],hex(a);return bytes.fromhex(r['hex']),r['id']
def ptr(a):return struct.unpack('<I',read(a,4)[0])[0]
identities={};observations=[];start=time.monotonic()
out=ROOT/'ElsaSceneResearch/ControllerState/live-idle-source-time-observations.json'
def checkpoint():
 report=dict(pid=status['pid'],module_base=status['module_base'],input_node=hex(node),identities=list(identities.values()),observations=observations,scope='Single active right-hand scalar contributor provenance; full file payload equality and clock alias. Reads are non-atomic; only equal stamped brackets may support same-frame matrix comparison. Other clips/actors not exhaustively observed.')
 out.write_text(json.dumps(report,indent=2),encoding='utf-8')
while time.monotonic()-start<90:
 nb,_=read(node,64);producer=struct.unpack_from('<I',nb,24)[0]
 pb,_=read(producer,0x34);assert struct.unpack_from('<I',pb,0x30)[0]==node
 count,table=struct.unpack_from('<I',pb,0x28)[0],struct.unpack_from('<I',pb,0x24)[0]
 assert 0<count<=16
 entries,_=read(table,count*8)
 for i in range(count):
  ctrl,packed=struct.unpack_from('<II',entries,i*8);cb,cid=read(ctrl,128)
  state,resolved=struct.unpack_from('<I',cb,0x50)[0],struct.unpack_from('<I',cb,0x74)[0]
  rtti=submit('RTTI',resolved)
  if rtti.get('name')!='.?AVClipProcessor@Samurai@@':
   observations.append(dict(elapsed=time.monotonic()-start,controller=hex(ctrl),boundary='Non-single ClipProcessor',rtti=rtti));continue
  rb,_=read(resolved,0x50);asset=struct.unpack_from('<I',rb,0x3c)[0];clock=struct.unpack_from('<I',rb,0x18)[0]
  blob=ptr(asset+0x3c)
  if blob not in identities:
   prefix,_=read(blob,128);candidate=known.get(prefix)
   identity=dict(blob=hex(blob),asset=hex(asset),resolved=hex(resolved),rtti=rtti,matched=False)
   if candidate:
    name,expected=candidate;actual=b''.join(read(blob+j,min(4096,len(expected)-j))[0] for j in range(0,len(expected),4096))
    identity.update(name=name,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),expected_sha256=hashlib.sha256(expected).hexdigest(),matched=actual==expected)
   identities[blob]=identity;checkpoint();print('SOURCE',identity.get('name','unknown'),'full match',identity['matched'],flush=True)
  sb,_=read(state,0x74);output=struct.unpack_from('<I',sb,0x6c)[0]
  assert output==clock,'Clock output alias changed'
  before,bid=read(clock,0x48)
  matrix=int(links[0]['matrix'],16);mb,mid=read(matrix,112)
  after,aid=read(clock,0x48)
  stamp=lambda b:struct.unpack_from('<H',b,0x20)[0]
  value=lambda b:struct.unpack_from('<f',b,0x34)[0]
  observations.append(dict(elapsed=time.monotonic()-start,controller=hex(ctrl),packed=hex(packed),state=hex(state),resolved=hex(resolved),blob=hex(blob),clock=hex(clock),source=identities[blob].get('name'),full_source_match=identities[blob]['matched'],state_local_time=struct.unpack_from('<f',sb,0x54)[0],state_range=list(struct.unpack_from('<2f',sb,0x3c)),clock_before=dict(stamp=stamp(before),time=value(before),request_id=bid),clock_after=dict(stamp=stamp(after),time=value(after),request_id=aid),index_matrix=dict(stamp=stamp(mb),values=list(struct.unpack_from('<12f',mb,0x40)),request_id=mid),same_stamp=stamp(before)==stamp(mb)==stamp(after)))
 checkpoint();time.sleep(.1)
report=dict(pid=status['pid'],module_base=status['module_base'],input_node=hex(node),identities=list(identities.values()),observations=observations,scope='Single active right-hand scalar contributor provenance; full file payload equality and clock alias. Reads are non-atomic; only equal stamped brackets may support same-frame matrix comparison. Other clips/actors not exhaustively observed.')
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SAVED',len(observations),'observations; same stamp',sum(o.get('same_stamp',False)for o in observations),flush=True)
try:
 import winsound
 winsound.MessageBeep()
except Exception:pass
