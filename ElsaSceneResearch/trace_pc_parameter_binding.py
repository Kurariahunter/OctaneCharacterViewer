"""Reproducible static binding/filter traces for the SHA-pinned installed PC executable."""
import json,hashlib,struct
from pathlib import Path
from exe_reader import read,disasm,b
ROOT=Path(__file__).parent
PIN='f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705'
if hashlib.sha256(b).hexdigest()!=PIN:raise ValueError('Executable identity changed')
regions=[('parameter_lookup',0x5439e0,0x6e),('typed_float_lookup',0x543a50,0x46),('parameter_name_getter',0x59fb50,0xe),('float_config',0x5a20c0,0x55),('float_factory',0x54fce0,0xb4),('track_weight_rebind',0x5a25f0,0x90),('key_blend_rebind',0x5a2720,0x9d),('referenced_clip_rebind',0x5a27c0,0xb0),('parameter_source_loader',0x777a70,0x316),('filter_constructor',0x4ce250,0x90),('filter_ref_factory',0x4ce2e0,0x78),('filter_cache_insert',0x4fabc0,0xbc),('filter_name_lookup',0x4e1790,0x1c),('filter_runtime_resolve',0x774500,0x74)]
manifest={'exe_sha256':PIN,'scope':'Static disassembly regions at confirmed function entries. Semantic claims are qualified in PC_PARAMETER_BINDING_FILTER_HANDOFF.md; static bytes do not establish actor state.','regions':[],'rtti':[]}
for name,va,size in regions:
 raw=read(va,size);file='binding-'+name+'-disassembly.txt';(ROOT/file).write_text(disasm(va,size));manifest['regions'].append(dict(name=name,va=hex(va),rva=hex(va-0x400000),size=size,sha256=hashlib.sha256(raw).hexdigest(),disassembly=file))
for vt,slots in [(0x1b38e4c,5),(0x1b38e94,5),(0x1b38ec4,5),(0x1b2f388,1)]:
 col=struct.unpack('<I',read(vt-4,4))[0];td=struct.unpack('<5I',read(col,20))[3];name=read(td+8,160).split(b'\0')[0].decode('ascii');manifest['rtti'].append(dict(vtable=hex(vt),complete_object_locator=hex(col),type_descriptor=hex(td),name=name,first_slots=[hex(x)for x in struct.unpack('<'+'I'*slots,read(vt,slots*4))]))
(ROOT/'pc-parameter-binding-filter-manifest.json').write_text(json.dumps(manifest,indent=2));print('Traced',len(regions),'regions;',len(manifest['rtti']),'RTTI types')
