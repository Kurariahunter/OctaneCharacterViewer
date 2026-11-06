import numpy as np
from evaluate_elsa_head import PROD,get
for i in [620,627]:
 p,_=PROD[i];print(i,list(zip(get(p,'DataNodeAttributes'),get(p,'DataNodeRefs'))))
s=open('validate_dress_reference_native.py').read();s=s.replace("assert err<1e-5,(typ,case,err)","\n  if err>=1e-5:\n   print(typ,[(label,float(np.max(abs(out-m)))) for label,m in [('AinvB',A@np.linalg.inv(B)),('invAB',np.linalg.inv(A)@B),('BinvA',B@np.linalg.inv(A)),('invBA',np.linalg.inv(B)@A),('invABboth',np.linalg.inv(A)@np.linalg.inv(B))]]);raise SystemExit")
exec(compile(s,'diagnostic','exec'))
