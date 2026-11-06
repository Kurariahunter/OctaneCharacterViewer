"""Validate the original uint16 mapping-copy routine with preallocated storage.

No allocator or serialized-property lookup is emulated by this test.
"""
import hashlib
import json
import struct
from pathlib import Path
from native_pc_lean_ik import u, sha
from exe_reader import read, disasm
from unicorn.x86_const import UC_X86_REG_ECX, UC_X86_REG_ESP, UC_X86_REG_EIP

B = 0x1C000000
u.mem_map(B, 0x20000)
OBJ, SRC, DST, STACK, STOP = [B+x for x in (0x1000, 0x3000, 0x6000, 0x18000, 0x1F000)]
cases = []
for values in ([0], [8, 2, 5], [65535, 4095, 4096, 65534, 0],
               list(reversed(range(62))), [(i*197+13) & 65535 for i in range(707)]):
    raw = struct.pack('<'+'H'*len(values), *values)
    u.mem_write(OBJ, b'\0'*0x60)
    u.mem_write(OBJ+0x10, struct.pack('<II', DST, len(values)))
    u.mem_write(SRC, raw)
    u.mem_write(DST, b'\xA5'*2048)
    # thiscall: source pointer, element count, allocation owner, final argument
    u.mem_write(STACK, struct.pack('<5I', STOP, SRC, len(values), 0x12345678, 0))
    u.reg_write(UC_X86_REG_ECX, OBJ)
    u.reg_write(UC_X86_REG_ESP, STACK)
    u.emu_start(0x4BEB30, STOP, count=100000)
    assert u.reg_read(UC_X86_REG_EIP) == STOP
    assert u.reg_read(UC_X86_REG_ESP) == STACK+20
    assert bytes(u.mem_read(DST, len(raw))) == raw
    assert bytes(u.mem_read(DST+len(raw), 16)) == b'\xA5'*16
    assert struct.unpack('<I', u.mem_read(OBJ, 4))[0] == 0
    assert struct.unpack('<II', u.mem_read(OBJ+0x10, 8)) == (DST, len(values))
    cases.append({'count':len(values), 'preserves_order_and_uint16_values':True,
                  'destination_guard_unchanged':True})

root = Path(__file__).parent/'RuntimeMapConstruction'
regions = {'map_constructor':(0x4CDE20,0x41),
           'serialized_map_loader':(0x4FD850,0x232),
           'uint16_property_loader':(0x4CF2F0,0x45),
           'uint16_copy':(0x4BEB30,0x38),
           'uint16_allocation':(0x4B5450,0x9A)}
manifest = {}
for name,(va,size) in regions.items():
    (root/(name+'.txt')).write_text(disasm(va,size)+'\n',encoding='utf-8')
    manifest[name] = {'va':hex(va),'size':size,'sha256':hashlib.sha256(read(va,size)).hexdigest()}
report = {'pass':True,'exe_sha256':sha,'cases':cases,'regions':manifest,
          'scope':'Complete 0x4BEB30 and original calls execute with non-null preallocated destination; no call-result stubs. Heap allocation, empty-array freeing, property lookup and full loader execution are not tested.'}
(root/'uint16-map-copy-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':True,'copy_cases':len(cases),'counts':[c['count'] for c in cases]}))
