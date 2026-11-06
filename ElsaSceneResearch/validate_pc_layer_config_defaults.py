"""Execute the complete native configuration-row array constructor."""
import json,struct
from pathlib import Path
from native_pc_lean_ik import u,sha
from exe_reader import read,disasm
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EDI,UC_X86_REG_EBX
B=0x1F000000;u.mem_map(B,0x20000)
ROWS=B+0x1000;STACK=B+0x18000;STOP=B+0x1F000
cases=[]
for count in [0,1,2,7]:
    u.mem_write(ROWS,b'\xA5'*1024)
    u.mem_write(STACK,struct.pack('<III',STOP,ROWS,count))
    u.reg_write(UC_X86_REG_ESP,STACK)
    u.emu_start(0x77A600,STOP,count=100000)
    assert u.reg_read(UC_X86_REG_EIP)==STOP
    assert u.reg_read(UC_X86_REG_ESP)==STACK+4 # cdecl arguments remain
    for i in range(count):
        row=bytes(u.mem_read(ROWS+i*64,64))
        strings=struct.unpack_from('<4I',row)
        assert strings==(0x1FA95A0,)*4
        assert read(strings[2],1)==b'\0' and read(strings[3],1)==b'\0'
        # Numeric fields copied from the original constant data; report exact values.
        assert struct.unpack_from('<f',row,0x10)[0]==0
        assert struct.unpack_from('<I',row,0x14)[0]==0
        assert struct.unpack_from('<I',row,0x1C)[0]==0
        assert struct.unpack_from('<I',row,0x24)[0]==0xFFFFFFFF
        assert struct.unpack_from('<H',row,0x3C)[0]==0x58
    assert bytes(u.mem_read(ROWS+count*64,16))==b'\xA5'*16
    cases.append({'count':count,'filter_and_mirror_names_empty':True,'guard_unchanged':True})
example=bytes(u.mem_read(ROWS,64))
default_paths=[]
for kind in ['absent_layers','empty_layers']:
    owner=B+0x5000;handle=B+0x6000
    u.mem_write(owner,b'\0'*128);u.mem_write(handle,b'\0'*64)
    u.mem_write(ROWS,b'\xA5'*1024);u.mem_write(STACK,b'\0'*128)
    u.mem_write(owner+0x24,struct.pack('<III',ROWS,0,7))
    u.mem_write(STACK+0x18,struct.pack('<I',0 if kind=='absent_layers' else handle))
    u.reg_write(UC_X86_REG_EDI,owner);u.reg_write(UC_X86_REG_EBX,0);u.reg_write(UC_X86_REG_ESP,STACK)
    u.emu_start(0x787329,0x787342,count=100000)
    assert u.reg_read(UC_X86_REG_EIP)==0x787342
    assert struct.unpack('<I',u.mem_read(owner+0x28,4))[0]==1
    assert bytes(u.mem_read(ROWS,64))==example
    assert bytes(u.mem_read(ROWS+64,16))==b'\xA5'*16
    default_paths.append({'case':kind,'row_count':1,'row_matches_native_default':True})
report={'pass':True,'exe_sha256':sha,'constructor':'0x77A600',
        'row_size':64,'cases':cases,'default_loader_paths':default_paths,'example_row_hex':example.hex(),
        'float_defaults':{hex(off):struct.unpack_from('<f',example,off)[0] for off in [0x10,0x18,0x20,0x28,0x2C,0x30,0x34,0x38]},
        'scope':'Complete original row-array constructor and helpers plus original absent/empty Layers loader window 0x787329..0x787342 execute without stubs. Loader-window array storage is preallocated; no heap allocation. Full outer file loader and explicit source-layer parsing remain statically traced.'}
out=Path(__file__).parent/'AuthoredFilters'
(out/'layer-config-default-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name,va,size in [('layer_row_constructor',0x77A600,0x80),
                     ('layer_array_resize',0x77E740,0x8F),
                     ('file_layer_selection',0x78730E,0x152)]:
    (out/(name+'.txt')).write_text(disasm(va,size)+'\n',encoding='utf-8')
print(json.dumps(report))
