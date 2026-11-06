"""Bounded native TransitionProcessor replay with cached clock/output nodes.

Runs53C800 and52D9B0. Event owners/callbacks are empty offline fixtures;
native completion flags execute, external callback effects are not modeled.
"""
import struct,math
from native_pc_lean_ik import u,sha
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_EDI
B=0x33000000;u.mem_map(B,0x20000)
P=B+0x1000;CLOCK=B+0x2000;OUT=B+0x3000;META=B+0x4000;STACK=B+0x18000;STOP=B+0x100
def put(a,v):u.mem_write(a,struct.pack('<I',v))
def node(a,value):
 u.mem_write(a,bytes(128));put(a+0x10,META);put(a+0x1c,META);u.mem_write(a+0x20,struct.pack('<H',1));u.mem_write(a+0x34,struct.pack('<f',value))
def prepare(header,clock,previous_output):
 if len(header)<96 or not all(math.isfinite(v)for v in (clock,previous_output)):raise ValueError('Invalid transition fixture')
 h=bytearray(header[:96]);offset=struct.unpack_from('<H',h,0x18)[0]
 if offset!=0x58 or h[0x1a:0x1c]!=b'\x01\x01':raise ValueError('Only observed one-input/output layout supported')
 h[0x38:0x48]=bytes(16);struct.pack_into('<II',h,0x58,CLOCK,OUT)
 u.mem_write(B,bytes(0x20000));put(META+0x20,1)
 for a in (0x213e6f0,0x213e6ec):put(a,0)
 u.mem_write(P,bytes(h));node(CLOCK,clock);node(OUT,previous_output)
 put(STACK,STOP);u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_ECX,P)
def execute(address):
 try:u.emu_start(address,STOP,count=500000)
 except Exception as e:raise RuntimeError('Transition stopped at '+hex(u.reg_read(UC_X86_REG_EIP)))from e
 if u.reg_read(UC_X86_REG_EIP)!=STOP:raise ValueError('Native transition instruction limit')
def step(header,clock,previous_output=0.):
 prepare(header,clock,previous_output);execute(0x53c800)
 value=struct.unpack('<f',u.mem_read(OUT+0x34,4))[0]
 if not math.isfinite(value):raise ValueError('Nonfinite transition output')
 return value,bytes(u.mem_read(P,96))
def activate(header,clock,*,start=0.,end=1.,duration=.1,clock_offset=0.,curve_parameter=1.,parameter_bits=2,mode=1,delay=0.):
 values=(start,end,duration,clock_offset,curve_parameter,delay)
 # Negative durations occur in the real activation path (configuration -1).
 # Preserve them; native curve evaluation handles nonpositive durations.
 if not all(math.isfinite(v)for v in values):raise ValueError('Invalid activation parameters')
 prepare(header,clock,0.)
 u.mem_write(STACK+4,struct.pack('<4f2I2f',start,end,duration,clock_offset,parameter_bits,mode,curve_parameter,delay))
 execute(0x52d9b0)
 return bytes(u.mem_read(P,96))
def resolve_duration(header,replacement):
 """Native770364..77038C: supplied duration replaces negative duration only."""
 if not math.isfinite(replacement):raise ValueError('Finite replacement required')
 prepare(header,0.,0.)
 controller=B+0x6000;put(controller+0x64,P)
 u.mem_write(STACK+0x1c,struct.pack('<f',replacement));u.reg_write(UC_X86_REG_EDI,controller)
 u.emu_start(0x770364,0x77038c,count=100000)
 if u.reg_read(UC_X86_REG_EIP)!=0x77038c:raise ValueError('Duration resolution did not return')
 return bytes(u.mem_read(P,96))
