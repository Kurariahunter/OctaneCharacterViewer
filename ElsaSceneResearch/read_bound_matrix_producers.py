"""Read-only snapshot of scene-bound matrix producer headers; never writes memory."""
import ctypes,json,struct,sys
from pathlib import Path
K=ctypes.WinDLL('kernel32',use_last_error=True)
K.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];K.OpenProcess.restype=ctypes.c_void_p
K.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
K.CloseHandle.argtypes=[ctypes.c_void_p]
h=K.OpenProcess(0x410,False,int(sys.argv[1]));assert h,ctypes.get_last_error()
def read(a,n):
 b=ctypes.create_string_buffer(n);got=ctypes.c_size_t()
 if not a or not K.ReadProcessMemory(h,a,b,n,ctypes.byref(got))or got.value!=n:return None
 return b.raw
def u(a):
 b=read(a,4);return struct.unpack('<I',b)[0]if b else None
def rtti(vt):
 col=u(vt-4)if vt else None;td=u(col+12)if col else None;b=read(td+8,192)if td else None
 return b.split(b'\0')[0].decode('ascii','replace')if b else None
try:
 root=Path(__file__).resolve().parent
 cap=root.parent/'OctaneLiveInspector/Captures/ce_skinbinding_20261020_213233_165612375.jsonl'
 es=[json.loads(l)for l in cap.read_text().splitlines()];base=int(es[0]['module_base'],16)
 groups={}
 for e in es:
  if e['event']=='skin_binding':groups.setdefault(e['binding']['object'],[]).append(e)
 candidates=[rs for rs in groups.values()if len(rs)==62];assert len(candidates)==1
 model=json.loads((root.parent/'OctaneCharacterViewer/Data/elsa-pc-mesh.json').read_text());rows=[]
 for e in candidates[0]:
  i=e['binding']['influence_index'];name=model['bones'][i]
  if not any(s in name for s in ['Hand','Index','Middle','Thumb']):continue
  n=int(e['binding']['matrix_node'],16);slot=int(e['binding']['slot'],16);p=u(n+24);vt=u(p)if p else None
  execute=u(vt+64)if vt else None;head=read(p,128)if p else None
  rows.append(dict(bone_index_candidate=i,bone_name_candidate=name,slot=hex(slot),slot_current=hex(u(slot)or 0),node=hex(n),producer=hex(p or 0),rtti=rtti(vt),
   execute_live=hex(execute or 0),execute_preferred=hex(execute-base+0x400000)if execute else None,
   producer_header_hex128=head.hex(' ')if head else None,node_header_hex112=(read(n,112)or b'').hex(' ')))
 out=dict(pid=int(sys.argv[1]),source_capture=str(cap),object_candidate=candidates[0][0]['binding']['object'],rows=rows,
  scope='Read-only later snapshot of captured 62-slot scene object. Bone names assigned by candidate file order, not independently verified. Reused/freed addresses must be rejected. No renderer parity proof.')
 (root/'ControllerState/scene-bound-matrix-producers.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps([dict(bone=r['bone_name_candidate'],rtti=r['rtti'],execute=r['execute_preferred'],slot_still_matches=int(r['slot_current'],16)==int(r['node'],16))for r in rows]))
finally:K.CloseHandle(h)
