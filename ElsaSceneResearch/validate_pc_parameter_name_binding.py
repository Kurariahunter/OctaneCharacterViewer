"""Native exact-name parameter lookup and isolated rebinding windows; synthetic containers."""
import json,struct,hashlib
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_EBX,UC_X86_REG_EAX,UC_X86_REG_EIP
BASE=0x18000000;u.mem_map(BASE,0x20000)
CONTAINER=BASE+0x1000;ARRAY=BASE+0x2000;QUERY=BASE+0x3000;QUERY_TEXT=QUERY+0x100;DEST=BASE+0x4000;STACK=BASE+0x18000;STOP=BASE+0x100

def w32(p,v):u.mem_write(p,struct.pack('<I',v))
def build(rows):
    u.mem_write(CONTAINER,b'\0'*256);w32(CONTAINER+0x94,ARRAY);w32(CONTAINER+0x98,len(rows));objects=[]
    # Synthetic runtime type registration: expected FloatParameter id 0x40 under mask 0xf0.
    w32(0x21c1960,0x40);w32(0x21c1964,0xf0)
    for i,row in enumerate(rows):
        if row is None:w32(ARRAY+i*4,0);objects.append(0);continue
        name,tag=row;obj=BASE+0x5000+i*0x300;block=obj+0x100;typ=obj+0x200
        u.mem_write(obj,b'\0'*128);u.mem_write(block,b'\0'*128);w32(obj+4,typ);w32(typ,tag);w32(obj+0xc,block);u.mem_write(block+0xc,name.encode('ascii')+b'\0');w32(ARRAY+i*4,obj);objects.append(obj)
    return objects

def query(text):
    u.mem_write(QUERY_TEXT,text.encode('ascii')+b'\0');w32(QUERY,QUERY_TEXT)
def lookup(entry,text):
    query(text);u.mem_write(STACK,struct.pack('<II',STOP,QUERY));u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,CONTAINER)
    u.emu_start(entry,STOP,count=3000)
    if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Lookup did not return')
    return u.reg_read(UC_X86_REG_EAX)
cases=[]
fixtures=[([],['Speed']),([None,('Speed',0x40),('Direction',0x40),('speed',0x40),('Speed',0x40)],['Speed','Direction','speed','SPEED','Missing','']),([('Speed',0x20),('Speed',0x40)],['Speed']),([('Speed',0x4f)],['Speed']),([('SpeedX',0x40),('Speed',0x40)],['Speed','SpeedX','Spee'])]
for rows,names in fixtures:
    objects=build(rows)
    for name in names:
        expected=next((objects[i]for i,row in enumerate(rows)if row is not None and row[0]==name),0)
        actual=lookup(0x5439e0,name)
        if actual!=expected:raise ValueError('Untyped exact-name lookup mismatch')
        expectedtyped=expected if expected and (struct.unpack('<I',u.mem_read(struct.unpack('<I',u.mem_read(expected+4,4))[0],4))[0]&0xf0)==0x40 else 0
        typed=lookup(0x543a50,name)
        if typed!=expectedtyped:raise ValueError('Typed exact-name lookup mismatch')
        cases.append(dict(rows=rows,query=name,result_index=objects.index(actual)if actual else None,typed_accepted=bool(typed)))
windows=[('track_weight',0x5a2636,0x5a2651,0xc),('key_blend_control',0x5a2773,0x5a278e,0x40),('referenced_clip_control',0x5a2813,0x5a282e,0x24)]
bindings=[];objects=build([('Speed',0x40),('Direction',0x40),('WrongType',0x20)])
for name,start,end,offset in windows:
    for text,expected in [('Speed',objects[0]),('Direction',objects[1]),('Missing',0),('WrongType',0)]:
        query(text);u.mem_write(DEST,b'\x7f'*128);u.mem_write(STACK,b'\0'*128);w32(STACK+0x1c,QUERY_TEXT)
        u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ESI,DEST);u.reg_write(UC_X86_REG_EBX,CONTAINER)
        u.emu_start(start,end,count=5000)
        if u.reg_read(UC_X86_REG_EIP)!=end:raise ValueError('Rebinding window did not finish')
        actual=struct.unpack('<I',u.mem_read(DEST+offset,4))[0]
        if actual!=expected:raise ValueError('Rebinding output mismatch')
        bindings.append(dict(window=name,query=text,accepted=bool(actual),destination_offset=hex(offset)))
report=dict(pass_=True,exe_sha256=sha,lookup_cases=len(cases),binding_window_cases=len(bindings),lookup='0x5439e0',typed_lookup='0x543a50',container_layout={'parameter_pointer_array':'0x94','parameter_count':'0x98','name_block_pointer_in_parameter':'0xc','characters_in_name_block':'0xc'},semantics=['Exact case-sensitive byte string comparison','First matching name returned; null table slots skipped','Typed lookup rejects first match if wrong runtime type; does not continue to later duplicate names','Track +0xc, key blend +0x40 and referenced clip +0x24 resolve through same typed name lookup'],cases=cases,binding_windows=bindings,scope='Original complete native lookup and typed getter; bounded rebinding windows with prebuilt temporary strings, ending before destruction. No callbacks or function-return stubs. Synthetic registration tags and table state; no real actor identification or complete object construction.')
report['pass']=report.pop('pass_');Path(__file__).with_name('pc-parameter-name-binding-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ('cases','binding_windows')},indent=2))
