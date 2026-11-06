from evaluate_elsa_head import N,get,allnodes
print('NETWORK',[(c['name'],str(c['value'])[:180]) for c in N['children'] if c['name'] not in ['Basis','DataNode','ProcessorNode']])
for p in allnodes(N,'ProcessorNode'):
 if int(p['value']) in [585,587,576,577,390,394,574,575]:print(p)
