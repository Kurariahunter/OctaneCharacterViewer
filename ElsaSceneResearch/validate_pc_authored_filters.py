"""Join real BCT filters to verified biped ports and exercise native blending."""
import hashlib,json,math,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'TupleDecoderResearch'))
from decode_tup_safe import decode
from native_pc_blend_replay import blend,sha
from probe_pc_blend_order import contributor,qaxis,mul,err
ROOT=Path(__file__).parent
source=Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/assets/gamedb/biped/characters/biped/biped.bct')
raw=source.read_bytes();doc=decode(raw)
assert doc['bytes_consumed']==len(raw)
assert doc['record_count']+1==struct.unpack_from('<I',raw,20)[0] # implicit root skipped by reader
filters={r['value']:r['extra'] for r in doc['records'] if r['name']=='Filter'}
assert len(filters)==92 and all(len(v)==968 for v in filters.values())
assert all(math.isfinite(x) for v in filters.values() for x in v)
audit=json.loads((ROOT/'RuntimeMapConstruction/serialized-runtime-map-audit.json').read_text(encoding='utf-8'))
mapping=audit['maps'][0]['rows']
base=mul(qaxis(0,37),qaxis(2,-21));delta=mul(qaxis(1,43),qaxis(0,-17))
rows=[];coverage={}
for name,values in filters.items():
    # Exercise every distinct coefficient encountered in this actual source map.
    representatives={}
    for row in mapping:
        port=row['filter_coefficient_index_port']
        assert port<len(values)
        representatives.setdefault(values[port],row)
    coverage[name]={'array_count':len(values),'mapped_slots':len(mapping),
                    'distinct_mapped_coefficients':sorted(representatives)}
    for value,row in representatives.items():
        c=contributor(delta,1,1,t=[.4,-.3,.2])
        c.update(filter_values=values,filter_index=row['filter_coefficient_index_port'],factor2c=.5)
        result=blend([contributor(base,0,t=[1.,2.,3.]),c],build_entries=True)
        weight=value*.5
        q=[v*weight for v in delta];q[3]+=1-weight
        length=math.sqrt(sum(v*v for v in q));q=[v/length for v in q]
        re=err(result[:4],mul(q,base))
        te=max(abs(v-(b+d*weight)) for v,b,d in zip(result[4:7],[1.,2.,3.],[.4,-.3,.2]))
        assert re<2e-6 and te<2e-6,(name,value,re,te)
        rows.append({'filter':name,'source_map_slot':row['source_slot'],
                     'port_index':row['filter_coefficient_index_port'],'coefficient':value,
                     'rotor_error':re,'translation_error':te})
for broken in [raw[:-1],raw[:0x740]]:
    try:decode(broken)
    except ValueError:pass
    else:raise AssertionError('Truncated BCT accepted')
out=ROOT/'AuthoredFilters';out.mkdir(exist_ok=True)
(out/'biped-filters.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(raw).hexdigest(),'filters':filters},indent=2),encoding='utf-8')
report={'pass':True,'exe_sha256':sha,'source_sha256':hashlib.sha256(raw).hexdigest(),
        'filter_count':len(filters),'mapped_filter_slot_checks':len(filters)*len(mapping),
        'native_cases':rows,'coverage':coverage,
        'max_rotor_error':max(r['rotor_error'] for r in rows),
        'max_translation_error':max(r['translation_error'] for r in rows),
        'scope':'Actual authored filter arrays and PC biped port indices; one native builder + native blend case per distinct mapped coefficient per filter. Synthetic base/delta inputs, compact source slot zero, flag39 additive, scalar2c=.5, no temporal fade. Does not identify active filters or prove full scene/actor composition. Mirror payload retained as separate uint32 type; not used as a float Filter.'}
(out/'authored-filter-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['native_cases','coverage']}))
print('native cases',len(rows))
