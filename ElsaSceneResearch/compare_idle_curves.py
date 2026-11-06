"""Bounded research comparison; reads originals, writes only this research directory."""
import ast, struct, math, json, zipfile, sys, hashlib
from pathlib import Path
sys.path.insert(0, 'F:/DisneyInfinityPortalTest/TupleDecoderResearch')
from decode_tup_safe import decode as container_decode
root=Path(__file__).parent
source=Path('C:/Users/Kurar/Disney Reloaded/Tools/YodaTimedHeadResearch/decode_timed_curves.py')
# Load only the previously reviewed pure decode/sample functions, bypassing the missing
# channel_probe helper and the original script's machine-specific main section.
decoder_text=source.read_text()
# Elsa's observed older layout interleaves uint16 descriptor-count/port pairs
# with descriptors. Retain all register and exact extent checks.
decoder_text=decoder_text.replace("codes=u('H'*num,p);p+=2*num;commands=[]", 'commands=[]')
decoder_text=decoder_text.replace('for code in codes:\n  desc=[]\n  for _ in range(code>>13):', "for _port in range(num):\n  descriptor_count,port=u('HH',p);p+=4\n  if descriptor_count&~0x1F:raise ValueError(f'unsupported descriptor flags {descriptor_count} at 0x{p-4:X}, port {port}')\n  descriptor_flags=descriptor_count&0x10;descriptor_count&=15\n  desc=[]\n  for _ in range(descriptor_count):")
decoder_text=decoder_text.replace("'port':code&8191", "'port':port")
decoder_text=decoder_text.replace("raise ValueError('unknown command')", "raise ValueError(f'unknown command 0x{op:04X} at payload offset 0x{p:X}')")
# Executable 0x5323A9..0x532479 confirms 8-byte 0x1xxx records.
decoder_text=decoder_text.replace('width=8 if op in (0x1090,0x1095) else 4', 'width=8 if op&0xF000==0x1000 else 4')
decoder_text=decoder_text.replace('if op not in (0x1090,0x1095,17,18,19,22,23,24,26):', 'if op&0xF000!=0x1000 and op not in (17,18,19,22,23,24,26):')
decoder_text=decoder_text.replace('refs=fields[1:] if op==0x1095 else fields[1:2]', 'refs=[fields[i+1] for i,shift in enumerate((4,2,0)) if ((op>>shift)&3)==1] if op&0xF000==0x1000 else fields[1:2]')
decoder_text=decoder_text.replace("'descriptors':desc", "'descriptors':desc,'record_flags':descriptor_flags")
tree=ast.parse(decoder_text)
functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('decode','sample')],type_ignores=[])
ns={'struct':struct,'math':math}
exec(compile(functions,str(source),'exec'),ns)
results=[]
with zipfile.ZipFile('G:/Downloads/fro_elsa.zip') as z:
 for info in z.infolist():
  if not info.filename.endswith('.oct') or '/motions/' not in info.filename: continue
  raw=z.read(info);doc=container_decode(raw)
  for index,node in enumerate(n for n in doc['records'] if n['name']=='ClipDataBlock'):
   b=bytes.fromhex(node['value']['hex']);name=Path(info.filename).stem
   row={'file':info.filename,'payload_bytes':len(b),'payload_sha256':hashlib.sha256(b).hexdigest(),'duration_seconds':struct.unpack_from('<f',b,4)[0] if len(b)>=8 else None}
   try:
    d=ns['decode'](b);err=d['max_continuity_error_quantization_units']
    row.update(status='supported_structure' if err<=3 else 'structure_with_continuity_warning',curves=len(d['curves']),registers=len(d['registers']),max_continuity_units=err,commands=d['commands'],static_command_bytes=d['static_commands_end']-d['static_commands_start'])
    if 'idle' in name:
     (root/(name+'.clipdata.bin')).write_bytes(b)
     (root/(name+'-decoded-curves.json')).write_text(json.dumps(d,indent=2))
     row['samples']=[{'time':row['duration_seconds']*k/4,'register_values':[ns['sample'](d,j,row['duration_seconds']*k/4) for j in range(len(d['registers']))]} for k in range(5)]
    for bad in [b[:10],b[:100],b[:12]+struct.pack('<I',len(b)+100)+b[16:]]:
     try:ns['decode'](bad)
     except (ValueError,struct.error,IndexError):pass
     else:raise AssertionError('Malformed payload accepted')
   except (ValueError,struct.error,IndexError) as e:row.update(status='unsupported',error=str(e))
   results.append(row)
report={'decoder_source':str(source),'decoder_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Structural curve decoding; no Elsa bone mapping or playback validation. Cubic samples are approximate, not native-evaluator output. Static command semantics not evaluated.','results':results}
(root/'timed-curve-comparison.json').write_text(json.dumps(report,indent=2))
from collections import Counter
print('STATUS',dict(Counter(r['status'] for r in results)))
for r in results:
 if 'idle' in r['file']:print(Path(r['file']).name,r['status'],r.get('error'),r.get('duration_seconds'),r.get('curves'),r.get('registers'),r.get('max_continuity_units'))
