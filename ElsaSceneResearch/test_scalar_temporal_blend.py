"""Offline native scalar-blender state tests; synthetic inputs, original instructions."""
import json,struct
from pathlib import Path
from native_pc_blend_replay import blend,sha,u,PROC

def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]

rows=[]
for previous,current in [(0.,.25),(.25,.5),(.5,.75),(.75,.5),(0.,1.),(.5,0.)]:
 c=dict(values=[10.]+[0.]*15,priority=5.,flag=0,weight=None,factor2c=None,factor30=current)
 observed=blend([c],scalar=True,previous_output=2.,previous_factor=previous,bypass_fade=False)[0]
 # 525450 converts an increasing cumulative fade into an incremental factor.
 increment=current if previous>current else ((current-previous)/(1-previous))
 expected=2. if current==0 else f(f(f(2.-10.)*f(1.-f(increment)))+10.)
 assert observed==expected,(previous,current,observed,expected)
 rows.append(dict(previous_factor=previous,current_factor=current,previous_output=2.,target=10.,observed=observed,expected=expected))
c=dict(values=[10.]+[0.]*15,priority=5.,flag=0,weight=None,factor2c=None,factor30=.5)
assert blend([c],scalar=True,previous_output=2.,previous_factor=.25,bypass_fade=True)==[10.]
assert struct.unpack('<I',u.mem_read(PROC+0x18,4))[0]&0x80000000
report=dict(passed=True,exe_sha256=sha,cases=rows,bypass_bit_preserved=True,scope='Synthetic cached single unflagged contributor, unit filter/factor2c and no default pose. Executes full native Float blender 4E3050 and fade helper525450. Does not establish unrecorded live previous state.')
(Path(__file__).parent/'ControllerState/scalar-temporal-native-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
