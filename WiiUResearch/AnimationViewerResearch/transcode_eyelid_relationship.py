from pathlib import Path
import json,base64,struct,sys,hashlib
P=Path('WiiUResearch/AnimationViewerResearch');tree=json.loads((P/'WiiUClips/fro_elsa.tree.json').read_text())
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
def get(n,k):return next((c['value']for c in n['children']if c['name']==k),None)
net=next(n for n in walk(tree)if n['name']=='SubNetwork');dn={int(n['value']):n for n in walk(net)if n['name']=='DataNode'}
node_id=int(sys.argv[1])if len(sys.argv)>1 else 34
blob=base64.b64decode(get(dn[node_id],'RelationshipDataBlock'));print('WiiU eyes blob',len(blob),hashlib.sha256(blob).hexdigest())
out=bytearray(blob)
def convert(p,n):out[p:p+n]=blob[p:p+n][::-1]
off=0
while True:
 count=struct.unpack_from('>H',blob,off+14)[0];end=off+struct.unpack_from('>I',blob,off+16)[0];cmd=off+struct.unpack_from('>I',blob,off+20)[0];ptrs=[off+v for v in struct.unpack_from('>'+str(count)+'I',blob,off+24)];ptrs.append(end)
 for at in range(off,off+12,4):convert(at,4)
 for at in range(off+12,off+16,2):convert(at,2)
 for at in range(off+16,off+24+4*count,4):convert(at,4)
 for at in range(cmd,ptrs[0],2):convert(at,2)
 for a,z in zip(ptrs,ptrs[1:]):
  word=struct.unpack_from('>I',blob,a+4)[0];dims=(word>>9)&2047;segments=word>>20
  for at in range(a,a+16+16*dims,4):convert(at,4)
  for at in range(a+16+16*dims,a+16+16*dims+2*segments+8*segments*dims,2):convert(at,2)
  assert (a+16+16*dims+2*segments+8*segments*dims+3)&~3==z
 nxt=struct.unpack_from('>I',blob,off+8)[0]
 print('stage',off,count,end,cmd,ptrs[0])
 if not nxt:break
 off=nxt
(P/'WiiUClips'/('elsa-eyelids.pc-endian.bin'if node_id==34 else f'relationship-{node_id}.pc-endian.bin')).write_bytes(out)
sys.path.insert(0,str(Path('ElsaSceneResearch').resolve()));from evaluate_pc_arms import DN,get as pcget
pc=bytes.fromhex(pcget(DN[node_id],'RelationshipDataBlock')['hex']);print('PC',len(pc),hashlib.sha256(pc).hexdigest());print('transcoded',hashlib.sha256(out).hexdigest(),'equal',bytes(out)==pc,'diff count',sum(a!=b for a,b in zip(out,pc)))

assert len(out)==len(pc)and bytes(out)==pc
(P/('eyelid-endian-equivalence.json'if node_id==34 else f'relationship-{node_id}-endian-equivalence.json')).write_text(json.dumps({'wiiu_sha256':hashlib.sha256(blob).hexdigest(),'transcoded_sha256':hashlib.sha256(out).hexdigest(),'pc_sha256':hashlib.sha256(pc).hexdigest(),'bytes':len(blob),'byte_equal':True},indent=2))


