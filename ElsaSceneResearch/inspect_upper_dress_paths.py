from evaluate_elsa_head import DN,PROD,get
for root in [650,655,660,668]:
 print('ROOT',root)
 def walk(i,depth=0):
  p=PROD.get(i)
  print(' '*depth,i,get(DN[i],'Type'),('producer '+str(p[0]['value'])+' '+get(p[0],'Type')+' '+p[1]) if p else str(get(DN[i],'Data')))
  if depth>=5 or not p:return
  refs=list(zip(get(p[0],'DataNodeAttributes'),get(p[0],'DataNodeRefs')))
  for a,v in refs:
   if PROD.get(v,(None,None))[0] is p[0]:continue
   print(' '*(depth+1),a);walk(v,depth+2)
 walk(root)
