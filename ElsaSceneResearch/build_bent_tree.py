import json
r=json.load(open('fro_elsa.bent-decoded.json'))['records'];root={'name':'Root','value':None,'children':[]};stack=[root]
for x in r:
 n=dict(x,children=[]);stack=stack[:x['depth']];stack[-1]['children'].append(n);stack.append(n)
json.dump(root,open('elsa-bent-tree.json','w'),indent=2)
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
for n in walk(root):
 if n['name']=='FileSet' and n['value']=='Models':print(json.dumps(n,indent=1))
for n in root['children']:
 if n['name']=='Channels':
  for c in n['children']:print(c['value'],[(x['name'],x['value']) for x in c['children']])
