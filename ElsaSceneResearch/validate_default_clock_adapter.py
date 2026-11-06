"""Compare viewer adapter with original mode/tail code and live captures."""
import json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'OctaneCharacterViewer'))
from native_default_clock import DefaultEngineClock,DemandClockConsumer
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
B=0x2A000000;u.mem_map(B,0x20000);P=B+0x1000;S=B+0x18000;STOP=B+0x1F000
cases=[]
for total in [0,123456,0x7ffffff0,0xfffffff0]:
 for cap in [60,100]:
  for raw in [0,1,16,100,250]:
   clock=DefaultEngineClock(total_ms=total,token=0xffffffff,cap_ms=cap)
   u.mem_write(P,b'\0'*128);u.mem_write(S,b'\0'*128)
   for off,value in [(0,clock.token),(4,raw),(0x18,total),(0x28,3),(0x34,cap)]:u.mem_write(P+off,struct.pack('<I',value))
   u.mem_write(P+0x24,struct.pack('<f',clock.seconds));u.mem_write(S+20,struct.pack('<I',STOP))
   u.mem_write(STOP+0x100,b'\xDB\xE3');u.emu_start(STOP+0x100,STOP+0x102,count=10)
   # Original normal selection and accumulation; EDI is the pre-capped input.
   from unicorn.x86_const import UC_X86_REG_EDI
   u.reg_write(UC_X86_REG_EDI,min(raw,cap));u.reg_write(UC_X86_REG_ESI,P);u.reg_write(UC_X86_REG_ESP,S)
   u.emu_start(0x67B02F,STOP,count=1000);assert u.reg_read(UC_X86_REG_EIP)==STOP
   clock.advance(raw)
   for off,fmt,value in [(0,'I',clock.token),(0x10,'I',clock.effective_delta_ms),(0x18,'I',clock.total_ms),(0x1c,'f',clock.delta_seconds),(0x20,'f',clock.previous_seconds),(0x24,'f',clock.seconds)]:
    assert struct.unpack('<'+fmt,u.mem_read(P+off,4))[0]==value
   cases.append({'total_ms':total,'cap_ms':cap,'raw_ms':raw})
replays=[]
for p in sorted((Path(__file__).parent.parent/'OctaneLiveInspector/Captures').glob('ce_*order_20261019_*.jsonl')):
 if 'clockorder_' not in p.name and 'publicationorder_' not in p.name:continue
 es=[json.loads(l)for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
 states=[bytes.fromhex(e['clock_hex88'])for e in es if e['event']=='clock_update']
 if len(states)<2:continue
 def ui(h,o):return struct.unpack_from('<I',h,o)[0]
 a=states[0];clock=DefaultEngineClock(total_ms=ui(a,0x18),token=ui(a,0),cap_ms=ui(a,0x34))
 count=0
 for h in states[1:]:
  assert ui(h,0x28)==3 and h[0x51]==0
  clock.cap_ms=ui(h,0x34);clock.advance(ui(h,4))
  assert (clock.token,clock.total_ms,clock.seconds,clock.delta_seconds)==(ui(h,0),ui(h,0x18),struct.unpack_from('<f',h,0x24)[0],struct.unpack_from('<f',h,0x1c)[0])
  count+=1
 replays.append({'capture':p.name,'transitions':count})
# Independent caches: skipped requests retain cache until actually demanded.
clock=DefaultEngineClock();a=DemandClockConsumer(lambda x:(x.seconds,x.token));b=DemandClockConsumer(lambda x:(x.seconds,x.token))
first=clock.publish();assert a.request(first)==b.request(first)==(0.,0)
clock.advance(16);assert a.request(clock.published)==(0.,0)
second=clock.publish();assert a.request(second)==(.01600000075995922,1)
assert b.evaluations==1
assert a.request(second)==a.value and a.evaluations==2
assert b.request(second)==a.value and b.evaluations==2
clock.publish();a.request(clock.published);assert a.evaluations==3 # new invalidation, unchanged time
report={'pass':True,'exe_sha256':sha,'native_cases':len(cases),'native_inputs':cases,'live_replays':replays,'lazy_cache_checks':True,
 'scope':'Normal-mode arithmetic only; original selection/accumulation window with pre-capped EDI. Explicit adapter publication serial is not native metadata stamp. Consumer uses test evaluator, not full native clip/controller.'}
(Path(__file__).parent/'ControllerState/default-clock-adapter-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k]for k in ('pass','native_cases','live_replays','lazy_cache_checks')}))
