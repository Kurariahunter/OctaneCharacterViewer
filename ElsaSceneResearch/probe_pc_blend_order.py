import math,json
from pathlib import Path
from native_pc_blend_replay import blend

def qaxis(axis,deg):
 q=[0.,0.,0.,math.cos(math.radians(deg)/2)];q[axis]=math.sin(math.radians(deg)/2);return q

def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def err(a,b):return min(max(abs(x-y)for x,y in zip(a,b)),max(abs(x+y)for x,y in zip(a,b)))
def contributor(q,flag,w=1,t=None):return dict(values=q+(t or [0.,0.,0.])+[1.]*9,priority=5.,flag=flag,weight=w,factor2c=1.,factor30=1.)
def main():
 base=mul(qaxis(0,37),qaxis(2,-21));delta=mul(qaxis(1,43),qaxis(0,-17));rows=[]
 for w in [0.,.25,.5,1.]:
  out=blend([contributor(base,0,t=[1.,2.,3.]),contributor(delta,1,w,t=[.4,-.3,.2])]);nd=[v*w for v in delta];nd[3]+=1-w;norm=math.sqrt(sum(v*v for v in nd));nd=[v/norm for v in nd]
  rows.append(dict(weight=w,predicted=out,base_times_nlerp_delta_error=err(out[:4],mul(base,nd)),nlerp_delta_times_base_error=err(out[:4],mul(nd,base)),translation_add_error=max(abs(a-b)for a,b in zip(out[4:7],[1+.4*w,2-.3*w,3+.2*w]))))
 print(json.dumps(rows,indent=2));(Path(__file__).parent/'pc-native-blend-controlled-probe.json').write_text(json.dumps(rows,indent=2))

if __name__=="__main__":main()
