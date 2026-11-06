from evaluate_elsa_head import N,DN,get,allnodes
p=next(p for p in allnodes(N,'ProcessorNode') if int(p['value'])==412)
for a,i in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')):
 if a=='InputScaleMultiplier':print(a,get(DN[i],'Data'))
