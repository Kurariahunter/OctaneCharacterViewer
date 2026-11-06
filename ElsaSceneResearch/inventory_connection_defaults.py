import json,struct,collections
from pathlib import Path
from evaluate_elsa_head import N,DN,get,stored
idx=bytes(get(N,'DefaultDataIndices'));raw=bytes(get(N,'DefaultData'));used=get(N,'ConnectionMapUsedDataNodes');assert len(idx)==2*len(used)
words=struct.unpack('<'+'H'*len(used),idx);f=struct.unpack('<'+'f'*(len(raw)//4),raw)
report={'scope':'Raw default table inventory. Low13-bit offset and high3-bit component-mask interpretation is a hypothesis, not executable-validated; no defaults applied.','index_bytes':len(idx),'default_bytes':len(raw),'used_slots':len(used),'word_counts':dict(collections.Counter(hex(w) for w in words)),'float_pool':f,'rows':[{'slot':s,'node':i,'type':get(DN[i],'Type'),'packed_word':hex(w),'stored':stored(DN[i]).tolist()} for s,(i,w) in enumerate(zip(used,words))]}
Path('connection-default-table-inventory.json').write_text(json.dumps(report,indent=2));print(report['word_counts'])
