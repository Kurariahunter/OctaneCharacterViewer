"""Original packed-contributor builder on preallocated synthetic tables."""
import json,struct,hashlib
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EBP
B=0x1b000000;u.mem_map(B,0x20000);PROC=B+0x1000;TABLE=B+0x2000;STACK=B+0x18000;STOP=B+0x100;NEXT=0

def w32(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
def reset():
 global NEXT
 NEXT=0;u.mem_write(PROC,b'\0'*128);u.mem_write(TABLE,b'\x7f'*4096);w32(PROC+0x24,TABLE);w32(PROC+0x2c,64)
def controller(priority,flag):
 global NEXT
 p=B+0x4000+NEXT*0x100;NEXT+=1;u.mem_write(p,b'\0'*128);u.mem_write(p+0x34,struct.pack('<f',priority));u.mem_write(p+0x39,bytes([flag]));return p
def call(ptr,source,index):
 u.mem_write(STACK,struct.pack('<IIII',STOP,ptr,source&0xffffffff,index&0xffffffff));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,PROC);u.emu_start(0x5440c0,STOP,count=100000)
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Builder did not return')
 count=struct.unpack('<I',u.mem_read(PROC+0x28,4))[0];return [struct.unpack('<II',u.mem_read(TABLE+i*8,8))for i in range(count)]
rows=[]
for source in [0,1,0x123,0xfff,0x1000,0x1abc,-1]:
 for index in [0,1,0xabc,0xfff,0x1000,0x1def,-1]:
  reset();ptr=controller(5.,0);out=call(ptr,source,index);expected=(source&0xfff)|((index&0xfff)<<12)
  if out!=[(ptr,expected)]:raise ValueError('Packed entry mismatch')
  rows.append(dict(source=source,filter_index=index,packed=hex(expected)))
# Native insertion path: original vector insert/move code, sufficient fixed capacity.
reset();inputs=[(5.,1),(2.,0),(5.,0),(7.,1),(2.,0),(5.,1)];expected=[];sortrows=[]
for order,(priority,flag)in enumerate(inputs):
 ptr=controller(priority,flag);source=order+3;index=100+order;expected.append((priority,flag,order,ptr,source|(index<<12)));expected.sort(key=lambda row:(row[0],row[1],row[2]))
 out=call(ptr,source,index)
 wanted=[(row[3],row[4])for row in expected]
 if out!=wanted:raise ValueError(('Insertion order mismatch',out,wanted))
 sortrows.append(dict(inserted_priority=priority,inserted_flag=flag,order=[row[2]for row in expected]))
reset();before=bytes(u.mem_read(TABLE,128));out=call(0,1,2);assert out==[]and bytes(u.mem_read(TABLE,128))==before
reset()
for i in range(50):call(controller(float(i),0),i,i+10)
before=bytes(u.mem_read(TABLE,512));out=call(controller(100.,0),100,100)
assert len(out)==50 and bytes(u.mem_read(TABLE,512))==before
registration=[];MAP=B+0xc000;INDICES=B+0xd000
for mapping in [[155,23,0],[0,4095,4096],[0xffff]]:
 for source in range(len(mapping)+1):
  reset();ptr=controller(5.,0);u.mem_write(MAP,b'\0'*128);w32(MAP+0x38,INDICES);w32(MAP+0x3c,len(mapping));u.mem_write(INDICES,struct.pack('<'+'H'*len(mapping),*mapping));u.mem_write(STACK,b'\0'*128)
  u.reg_write(UC_X86_REG_ECX,PROC);u.reg_write(UC_X86_REG_EBP,MAP);u.reg_write(UC_X86_REG_ESI,source);u.reg_write(UC_X86_REG_EBX,ptr);u.reg_write(UC_X86_REG_ESP,STACK)
  u.emu_start(0x4ceabe,0x4ceadc,count=100000)
  if u.reg_read(UC_X86_REG_EIP)!=0x4ceadc:raise ValueError('Registration window did not finish')
  value=mapping[source]if source<len(mapping)and mapping[source]!=0xffff else 0xffffffff
  actual=struct.unpack('<II',u.mem_read(TABLE,8));expected=source|((value&0xfff)<<12)
  if actual!=(ptr,expected):raise ValueError('Mapped registration mismatch')
  registration.append(dict(source_index=source,map_values=mapping,packed_filter_index=(value&0xfff),sentinel_or_out_of_range=value==0xffffffff))
report=dict(pass_=True,exe_sha256=sha,entry='0x5440c0',entry_size=0xce,entry_sha256=hashlib.sha256(read(0x5440c0,0xce)).hexdigest(),pack_formula='(argument2 & 0xfff) | ((argument3 & 0xfff) << 12)',constructor_initial_upper_byte=0,packing_cases=rows,insertion_cases=sortrows,null_controller_noop=True,cap_50_enforced=True,scope='Complete native builder with preallocated capacity 64; real native insertion and move helpers execute. No heap allocation, actor state or full source connection loader. Finite priorities and boolean flags only; source-to-authored-port mapping still unresolved.')
report['registration_window']={'start':'0x4ceabe','end':'0x4ceadc','map_pointer_field':'0x38','map_count_field':'0x3c','element_type':'uint16','cases':registration};report['pass']=report.pop('pass_');Path(__file__).with_name('pc-contributor-entry-builder-validation.json').write_text(json.dumps(report,indent=2));Path(__file__).with_name('pc-contributor-entry-builder-disassembly.txt').write_text(disasm(0x5440c0,0xce));print(json.dumps({k:v for k,v in report.items()if k not in ('packing_cases','insertion_cases','registration_window')},indent=2));print('packing cases',len(rows),'sorted insertion cases',len(sortrows),'mapped registration cases',len(registration))
