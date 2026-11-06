"""Original resolver through lookup, ending before reference assignment."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import disasm
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EDI
B=0x1E000000;u.mem_map(B,0x20000)
CTRL=B+0x1000;HANDLE=B+0x2000;CONFIGOWNER=B+0x3000;ROWS=B+0x4000
MAP=B+0x5000;OWNER=B+0x6000;STACK=B+0x18000
def put(a,v):u.mem_write(a,struct.pack('<I',v))
def string(a,text):
    # Resolver tests string length at chars-12; lookup consumes a pointer to chars.
    put(a,len(text));u.mem_write(a+12,text.encode('ascii')+b'\0');return a+12
def hashname(text):
    h=0
    for c in text.encode('ascii'):h=(h*33+c)&0xffffffff
    return h
def cache(offset,name,value,address):
    table=OWNER+offset;buckets=address;entry=address+0x100;nameptr=string(address+0x200,name)
    put(table+0x1c,1);put(table+0x14,buckets);put(buckets,entry)
    put(entry,0);put(entry+4,hashname(name));put(entry+8,nameptr);put(entry+12,value)
cases=[]
for label,filtername,mirrorname,condition in [
    ('both_named','HeadTurn','Mirror','valid'),('filter_only','HeadTurn','','valid'),
    ('mirror_only','','Mirror','valid'),('empty_both','','','valid'),
    ('missing_filter','Unknown','Mirror','valid'),('case_sensitive','headturn','Mirror','valid'),
    ('missing_mirror','HeadTurn','Unknown','valid'),('no_handle','HeadTurn','Mirror','no_handle'),
    ('no_config_owner','HeadTurn','Mirror','no_config_owner'),
    ('row_out_of_bounds','HeadTurn','Mirror','bad_row'),
    ('no_mapping','HeadTurn','Mirror','no_mapping'),('no_map_owner','HeadTurn','Mirror','no_owner')]:
    u.mem_write(B,b'\0'*0x20000)
    put(CTRL+0x78,HANDLE);put(HANDLE+0x24,CONFIGOWNER);put(HANDLE+0x28,1)
    put(CONFIGOWNER+0x24,ROWS);put(CONFIGOWNER+0x28,2)
    put(ROWS+0x40+8,string(B+0x9000,filtername));put(ROWS+0x40+12,string(B+0x9200,mirrorname))
    # Deliberately conflicting row zero: verifies selected-row lookup, not a parent fallback.
    put(ROWS+8,string(B+0x9400,'Unknown'));put(ROWS+12,string(B+0x9600,'Unknown'))
    put(CTRL+0x20,MAP);put(MAP+12,OWNER)
    cache(0xc,'HeadTurn',B+0xC000,B+0xA000);cache(0x44,'Mirror',B+0xC100,B+0xB000)
    if condition=='no_handle':put(CTRL+0x78,0)
    elif condition=='no_config_owner':put(HANDLE+0x24,0)
    elif condition=='bad_row':put(HANDLE+0x28,2)
    elif condition=='no_mapping':put(CTRL+0x20,0)
    elif condition=='no_owner':put(MAP+12,0)
    u.reg_write(UC_X86_REG_ECX,CTRL);u.reg_write(UC_X86_REG_ESP,STACK)
    u.emu_start(0x774500,0x774559,count=100000)
    assert u.reg_read(UC_X86_REG_EIP)==0x774559
    esp=u.reg_read(UC_X86_REG_ESP)
    selected=struct.unpack('<I',u.mem_read(esp+12,4))[0]
    mirror=u.reg_read(UC_X86_REG_EDI)
    expected=B+0xC000 if condition=='valid' and filtername=='HeadTurn' else 0
    expected_mirror=B+0xC100 if condition=='valid' and mirrorname=='Mirror' else 0
    assert (selected,mirror)==(expected,expected_mirror),(label,selected,mirror)
    cases.append({'case':label,'filter_selected':bool(selected),'mirror_selected':bool(mirror)})
out=Path(__file__).parent/'AuthoredFilters'
report={'pass':True,'exe_sha256':sha,'cases':cases,
        'scope':'Original resolver 0x774500..0x774559 including complete config getter and native exact-name hash-table lookups; prebuilt owner caches and config strings, no call-result stubs. Stops before smart-reference assignment. Does not prove how configuration rows are authored/inherited upstream.'}
(out/'native-filter-selection-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name,va,size in [('filter_selection',0x774500,0x74),('config_row_getter',0x76cc50,0x19),('filter_hash_lookup',0x13819f0,0xb4)]:
    (out/(name+'.txt')).write_text(disasm(va,size)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'cases':len(cases),'scope':report['scope']}))
