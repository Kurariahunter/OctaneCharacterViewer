from exe_reader import *
import json
from pathlib import Path
for name,va,size in [('channel-declaration-loader',0x787480,0x1f1),('default-table-allocation',0x4b41d0,0x100),('default-transform-getter',0x4b23d0,0x93),('default-float-lookup',0x4e339f,0x73),('scene-default-table-linkage',0x50125f,0x70)]:Path(name+'-disassembly.txt').write_text(disasm(va,size))
assert read(0x1b35cb4,7).split(b'\0')[0]==b'Weight'
assert struct.unpack('<f',read(0x1b24124,4))[0]==1
report={'scope':'Static loader trace; no full BENT loader or runtime selection execution.','per_channel_stride':20,'fields':{'name':0,'field_at_4':'property string0x1b4c390; not interpreted here','priority':8,'weight':12,'channel_index':16},'loader_range':['0x787480','0x787670'],'missing_property_defaults':{'priority':0,'weight':1,'channel_index':-1},'weight_property_address':'0x1b35cb4','weight_fallback_constant':'0x1b24124','limitations':['Priority sort direction and equal-priority handling unverified.','ChannelIndex is parsed, not verified as enabled runtime state.','Missing runtime Weight and default Weight are not the same as proof of a playing layer.']}
Path('channel-declaration-loader-findings.json').write_text(json.dumps(report,indent=2));print(report)
