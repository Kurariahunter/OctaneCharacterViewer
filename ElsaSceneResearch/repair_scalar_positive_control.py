from pathlib import Path
p=Path('compare_live_particle_scalar.py');s=p.read_text().replace('for synthetic in [False,True]:','for synthetic in [False]:')
s=s.replace("# Execute unchanged sampler mechanics",'''# Positive control: unmodified arithmetic block with explicit nonzero inputs.
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_XMM1,UC_X86_REG_XMM2,UC_X86_REG_XMM4,UC_X86_REG_XMM5,UC_X86_REG_XMM6,UC_X86_REG_XMM7
pack=lambda x:int.from_bytes(struct.pack('<f',x)+bytes(12),'little')
unpack=lambda x:struct.unpack('<f',int(x).to_bytes(16,'little')[:4])[0]
positive=[]
for value in [1.,.5]:
 u.mem_write(BASE+0x1000+0x98,struct.pack('<f',value));stack=BASE+0x1e000
 u.mem_write(stack+0x90,struct.pack('<f',1));u.mem_write(stack+0xa4,struct.pack('<f',1));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,BASE+0x1000)
 for reg,x in [(UC_X86_REG_XMM1,2),(UC_X86_REG_XMM2,3),(UC_X86_REG_XMM4,0),(UC_X86_REG_XMM5,0),(UC_X86_REG_XMM6,0),(UC_X86_REG_XMM7,0)]:u.reg_write(reg,pack(x))
 u.emu_start(0x4a21ef,0x4a222b,count=100)
 positive.append([unpack(u.reg_read(reg)) for reg in [UC_X86_REG_XMM4,UC_X86_REG_XMM5,UC_X86_REG_XMM6]])
assert positive==[[2.,3.,1.],[1.,1.5,.5]],positive
# Execute unchanged sampler mechanics''')
s=s.replace("assert results[1]['max_position_difference']>1e-8,'Positive control failed to show sensitivity'","assert positive[0]!=positive[1]")
s=s.replace("'moving_anchor_fixtures':results,","'moving_anchor_fixtures':results,'arithmetic_block_positive_control':{'range':['0x4a21ef','0x4a222b'],'outputs':positive},")
s=s.replace('Synthetic tip7 demonstrates the fixture can detect an effect.','An unmodified arithmetic-block positive control demonstrates sensitivity to slot98 when that block receives nonzero inputs.')
s=s.replace('Synthetic tip7 is sensitivity test only, never a source fix.','Arithmetic-block sensitivity test is separate from full source configurations.')
p.write_text(s)
