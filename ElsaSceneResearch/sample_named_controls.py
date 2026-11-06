"""Named controller samples, not final skeleton transforms."""
import ast,sys,json,struct,csv,math
from pathlib import Path
ROOT=Path(__file__).parent
# Reuse isolated native setup without rerunning its standalone report.
t=ast.parse((ROOT/'validate_elsa_native_curves.py').read_text());setup=[]
for n in t.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='rows' for x in n.targets):break
 setup.append(n)
env={'__file__':str(ROOT/'validate_elsa_native_curves.py')};exec(compile(ast.Module(body=setup,type_ignores=[]),'native-setup','exec'),env)
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ECX
u=env['u']
def native_rotation(angles):
 inp=0x10001000;out=inp+32;stack=0x10010000;stop=0x10000100
 u.mem_write(inp,struct.pack('<3f',*angles));u.mem_write(out,b'\0'*16);u.mem_write(stack,struct.pack('<II',stop,out));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,inp)
 u.emu_start(0x40e180,stop,count=20000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('rotation did not return')
 q=struct.unpack('<4f',u.mem_read(out,16))
 if abs(sum(x*x for x in q)-1)>1e-5:raise ValueError('nonunit rotation')
 return q
mapping=json.loads((ROOT/'elsa-control-mapping.json').read_text());allrows=[]
for clipname in ['elsa_bm_idle_active','elsa_bm_idle_passive']:
 clip=next(c for c in mapping['idle_clips'] if Path(c['file']).stem==clipname)
 selected=[c for c in clip['commands'] if c['model_control']['basis'] in ('Cntrl_Head_Grp','Cntrl_Neck_Grp')]
 b=(ROOT/(clipname+'.clipdata.bin')).read_bytes();d=json.loads((ROOT/(clipname+'-decoded-curves.json')).read_text());n=struct.unpack_from('<H',b,10)[0];offsets=struct.unpack_from('<'+'I'*(n+2),b,12);duration=struct.unpack_from('<f',b,4)[0];pool=offsets[0]
 assert (len(b)-pool)%4==0
 constants=struct.unpack_from('<'+'f'*((len(b)-pool)//4),b,pool)
 for frame in range(61):
  time=duration*frame/60;cache={}
  def value(ref,dynamic):
   if not dynamic:
    if not 0<=ref<len(constants):raise ValueError('static operand out of range')
    v=constants[ref]
   else:
    if not 0<=ref<len(d['registers']):raise ValueError('register out of range')
    r=d['registers'][ref];ci=r['curve']
    if ci not in cache:
     start=offsets[ci+2];end=offsets[ci+3] if ci+3<len(offsets) else pool
     cache[ci]=env['native_curve'](b[start:end],time,len(d['curves'][ci]['metadata']))
    v=cache[ci][r['component']]
   if not math.isfinite(v):raise ValueError('nonfinite input')
   return v
  for command in selected:
   rotations=[x for x in command['descriptors'] if x[0]&0xf000==0x1000]
   if len(rotations)!=1:raise ValueError('unexpected head/neck rotation count')
   fields=rotations[0];op=fields[0]
   if ((op>>6)&7)!=2:raise ValueError('unsupported Euler convention')
   flags=[(op>>shift)&3 for shift in (4,2,0)]
   if any(x not in (0,1) for x in flags):raise ValueError('unsupported axis source flags')
   angles=[value(ref,flag==1) for ref,flag in zip(fields[1:],flags)];q=native_rotation(angles)
   allrows.append({'clip':clipname,'time':time,'control':command['model_control']['basis'],'port':command['port'],'data_node':command['model_control']['data_node'],'opcode':hex(op),'x_radians':angles[0],'y_radians':angles[1],'z_radians':angles[2],'source_qx':q[0],'source_qy':q[1],'source_qz':q[2],'source_qw':q[3]})
with (ROOT/'elsa-head-neck-native-samples.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=allrows[0].keys());w.writeheader();w.writerows(allrows)
(ROOT/'named-control-samples.json').write_text(json.dumps({'scope':'Original curve evaluator and convention-2 rotation routine sampled in isolated emulation. Source controller rotations only: no procedural graph evaluation, final skin-bone mapping, Unity coordinate conversion or layer composition.','sample_rows':len(allrows),'samples':allrows},indent=2))
print('ROWS',len(allrows),'FINITE_UNIT_CONTROLLER_QUATERNIONS',True)
