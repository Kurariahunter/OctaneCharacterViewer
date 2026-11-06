from read_pc_idle_files import *
p=R/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent';root=tree(tuple_decode(p.read_bytes())['records'])
def rec(n,anc=()):
 if n['name']in ['Layer','Filter'] or 'GroupRunForward'==n.get('value'):
  print('PATH',[(x['name'],str(x.get('value'))[:75])for x in anc[-3:]])
  print(json.dumps(n)[:16000])
 for c in n.get('children',[]):rec(c,anc+(n,))
rec(root)
