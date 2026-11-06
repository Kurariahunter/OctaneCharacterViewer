from evaluate_elsa_head import DN,PROD,get
seen=set()
def walk(i,depth):
 if i in seen or depth>8:return
 seen.add(i);prod=PROD.get(i)
 if not prod:return
 p,a=prod;print(i,p['value'],get(p,'Type'),a)
 if get(p,'Type').startswith('IK'):return
 for label,v in zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs')):
  if PROD.get(v,(None,None))[0] is not p:walk(v,depth+1)
walk(615,0);walk(622,0)
