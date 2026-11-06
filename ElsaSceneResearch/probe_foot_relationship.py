"""Bounded relationship-table probe, with native accessor checks; not evaluation."""
import sys,struct,json,hashlib
from pathlib import Path
from evaluate_elsa_head import DN,get
from native_leg_ik import u
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_EAX
ROOT=Path(__file__).parent
b=bytes.fromhex(get(DN[39],'RelationshipDataBlock')['hex']);assert b==bytes.fromhex(get(DN[66],'RelationshipDataBlock')['hex'])
def take(fmt,offset):
 size=struct.calcsize('<'+fmt)
 if offset<0 or offset+size>len(b):raise ValueError('relationship field out of bounds')
 return struct.unpack_from('<'+fmt,b,offset)
obj=0x10001000;blob=0x10004000;stack=0x10010000;stop=0x10000100;oa=0x10003000;ob=oa+4
u.mem_write(obj,b'\0'*128);u.mem_write(blob,b);u.mem_write(obj+0x3c,struct.pack('<I',blob))
def native(va,args):
 u.mem_write(oa,b'\0'*8);u.mem_write(stack,struct.pack('<'+'I'*(len(args)+1),stop,*args));u.reg_write(UC_X86_REG_ECX,obj);u.reg_write(UC_X86_REG_ESP,stack);u.emu_start(va,stop,count=10000)
 if u.reg_read(UC_X86_REG_EIP)!=stop:raise ValueError('native accessor did not return')
 return u.reg_read(UC_X86_REG_EAX)
stride=take('I',8)[0];groups=take('H',12)[0];sections=[]
for section in (0,1):
 base=section*stride;rows=[]
 for group in range(groups):
  rel=take('I',base+0x14+4*group)[0];p=base+rel;nin,nout=take('HH',p);rows.append({'group':group,'header_offset':p,'first_count':nin,'second_count':nout})
 native(0x503c90,[section,oa,ob]);actual=struct.unpack('<II',u.mem_read(oa,8));expected=(max(x['first_count'] for x in rows),max(x['second_count'] for x in rows));assert actual==expected
 sections.append({'section':section,'base':base,'group_headers':rows,'native_503c90_counts':list(actual)})
# Output record-list accessor uses second section, group0.
p=stride+take('I',stride+0x14)[0];n=take('H',p+2)[0];count=take('H',p+n*2+6)[0];offset=p+n*2+8;native(0x503e00,[oa,ob,0]);actual=struct.unpack('<I',u.mem_read(oa,4))[0];ptr=struct.unpack('<I',u.mem_read(ob,4))[0];assert ptr==blob+offset and actual==count
report={'scope':'Native-tested metadata access only. Counts/offsets are not a full relationship semantic specification.','blob_length':len(b),'blob_sha256':hashlib.sha256(b).hexdigest(),'shared_nodes':[39,66],'section_stride':stride,'root_group_count':groups,'sections':sections,'native_output_records':{'data_offset':offset,'count':count},'runtime':'0x54c9a0','vtable':'0x1b349ac','constructor':'0x53cc90','allocated_base_size':'0x68 plus appended arrays','helpers':{'input_evaluation':'0x544e00','output_writes':'0x53d2b0','completion_or_cache_helper':'0x53e920','record_access':'0x503e00'},'unresolved':'Record meanings, interpolation/composition, cache initialization and complete original foot-target execution.'}
(ROOT/'foot-relationship-structure.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
