import json
root=json.load(open('elsa-bent-tree.json'))
def walk(n,parents=()):
 yield n,parents
 for c in n['children']:yield from walk(c,parents+((n['name'],n['value']),))
for n,parents in walk(root):
 if n['name'] in ['Layer','Filter']:
  print(parents[-3:],json.dumps(n,separators=(',',':'))[:850])
