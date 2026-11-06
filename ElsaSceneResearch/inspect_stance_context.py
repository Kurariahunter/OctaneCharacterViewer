import json
r=json.load(open('fro_elsa.bent-decoded.json'))['records'];stack=[]
for i,x in enumerate(r):
 while stack and stack[-1]['depth']>=x['depth']:stack.pop()
 if x['name']=='Filename' and x['value'] in ['motions/elsa_bm_idle_active.oct','motions/elsa_bm_idle_passive.oct']:
  print('PARENTS',[(p['name'],p['value']) for p in stack]);fs=next(p for p in reversed(stack) if p['name']=='FileSet');j=r.index(fs);end=next((k for k in range(j+1,len(r)) if r[k]['depth']<=fs['depth']),len(r));print(json.dumps(r[j:min(j+65,end)],indent=1))
 stack.append(x)
print('TOP',[(x['name'],x['value']) for x in r if x['depth']<=2][:55])
