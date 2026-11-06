"""Match bounded live ClipDataBlock prefixes to extracted PC file candidates."""
import hashlib,json,sys
from pathlib import Path
from read_pc_idle_files import tuple_decode
R=Path(__file__).parent

def match(capture,output):
    events=[json.loads(l)for l in Path(capture).read_text().splitlines()]
    snapshots={}
    for e in events:
        if e.get('event') in ('referenced_sample','group_dispatch','blend_before') and e.get('track') and e.get('prefix_hex256'):
            key=str(e.get('asset'))+':'+str(e.get('blob'))
            snapshots[key]=dict(key=key,prefix_hex256=e['prefix_hex256'],controller=e['track'],sequence=e['sequence'])
        if e.get('event')=='clip_sample' and e.get('prefix_hex256'):
            key=str(e.get('asset'))+':'+str(e.get('blob'))
            snapshots[key]=dict(key=key,prefix_hex256=e['prefix_hex256'],controller=e['object'],sequence=e['sequence'])
        if e.get('event')=='group_dispatch' and e.get('referenced_prefix_hex256'):
            key=str(e.get('referenced_asset'))+':'+str(e.get('referenced_blob'))
            snapshots[key]=dict(key=key,prefix_hex256=e['referenced_prefix_hex256'],controller=e['child'],sequence=e['sequence'])
        for c in e.get('contributions',{}).values():
            s=c.get('controller_state',{});f=s.get('source_fingerprint')
            if f:snapshots[f['key']]=dict(f,controller=c['controller'],sequence=e['sequence'])
    catalog=[];errors=[]
    for p in (R/'InstalledGameAssetCheck').rglob('*.oct'):
        try:
            for i,v in enumerate(x['value']for x in tuple_decode(p.read_bytes())['records']if x['name']=='ClipDataBlock'):
                b=bytes(v)if isinstance(v,list)else bytes.fromhex(v['hex'])
                catalog.append(dict(path=str(p.resolve()),block=i,size=len(b),sha256=hashlib.sha256(b).hexdigest(),payload=b))
        except (ValueError,KeyError,TypeError,IndexError) as ex:errors.append(dict(path=str(p),error=str(ex)))
    rows=[]
    for key,f in snapshots.items():
        raw=f.get('prefix_hex256');prefix=bytes.fromhex(raw)if raw else b''
        candidates=[]
        for c in catalog:
            size=min(256,c['size'])
            if len(prefix)==256 and size>=32 and c['payload'][:size]==prefix[:size]:
                candidates.append(dict({k:v for k,v in c.items()if k!='payload'},compared_bytes=size,entire_file_block_covered=c['size']<=256))
        rows.append(dict(key=key,controller=f['controller'],sequence=f['sequence'],prefix_size=len(prefix),
            prefix_sha256=hashlib.sha256(prefix).hexdigest()if prefix else None,candidates=candidates))
    report=dict(capture=str(Path(capture).resolve()),snapshots=len(rows),catalog_blocks=len(catalog),catalog_errors=errors,matches=rows,
        scope='At most256 bytes compared. For file blocks shorter than256, compare the complete file block and ignore trailing captured bytes outside that candidate; minimum32 bytes. Candidate equality is not allocation-size or unique actor proof. Larger blocks remain prefix-only. Search limited to extracted PC OCT files under InstalledGameAssetCheck. Unmatched data may be uncatalogued or runtime transformed; no decoder failure inferred.')
    Path(output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

if __name__=='__main__':
    r=match(sys.argv[1],sys.argv[2]if len(sys.argv)>2 else R/'ControllerState/live-clip-prefix-matches.json')
    print(json.dumps({k:v for k,v in r.items()if k not in ('matches','scope','catalog_errors')}))
