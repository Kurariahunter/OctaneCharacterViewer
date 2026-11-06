import struct,json
from pathlib import Path
from native_pc_lean_ik import pe,exe,sha
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
raw=exe.read_bytes();md=Cs(CS_ARCH_X86,CS_MODE_32);strings=[];pos=0
while True:
 pos=raw.find(b'Filter\0',pos)
 if pos<0:break
 if pos==0 or raw[pos-1]==0:
  va=pe.OPTIONAL_HEADER.ImageBase+pe.get_rva_from_offset(pos);strings.append(va)
 pos+=1
refs=[]
for va in strings:
 needle=struct.pack('<I',va)
 for section in pe.sections:
  if not section.Characteristics&0x20000000:continue
  code=section.get_data();offset=0
  while True:
   index=code.find(needle,offset)
   if index<0:break
   offset=index+1
   if index==0 or code[index-1]not in [0x68,0xb8,0xb9,0xba,0xbb,0xbe,0xbf]:continue
   address=pe.OPTIONAL_HEADER.ImageBase+section.VirtualAddress+index-1
   instructions=list(md.disasm(code[index-1:index+40],address))
   if instructions and instructions[0].size==5:refs.append({'string_address':hex(va),'candidate_reference':hex(address),'instructions':[f'{i.address:08x} {i.mnemonic} {i.op_str}'for i in instructions]})
report={'exe_sha256':sha,'scope':'Exact Filter string immediate-reference candidates only. Not established loader/filter-weight semantics.','strings':[hex(v)for v in strings],'references':refs}
Path(__file__).with_name('pc-filter-string-reference-candidates.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
