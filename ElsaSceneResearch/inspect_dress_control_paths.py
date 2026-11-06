from decode_header_paths import paths
from evaluate_elsa_head import DN,PROD,get
for i in [565,566,605,606,649,650,654,655,615,622,620,627]:
 p=PROD.get(i);print(i,paths[i], get(p[0],'Type') if p else None, list(zip(get(p[0],'DataNodeAttributes'),get(p[0],'DataNodeRefs'))) if p else None)
