"""Build the source tree used by native graph research from parsed BinaryTup."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'OCTParser'))
from read_binary_tup import parse

def read_tree(path):
 items=[]
 for n in parse(path)['nodes']:
  v=n['name']if n['kind']==1 else n['value'];v=v['base64']if isinstance(v,dict)and 'base64'in v else v;item={'name':n['key'],'value':v,'children':[]};items.append(item)
  if n['parent']is not None:items[n['parent']]['children'].append(item)
 return {'name':'root','value':None,'children':[items[0]]}
if __name__=='__main__':Path(sys.argv[2]).write_text(json.dumps(read_tree(sys.argv[1])),encoding='utf-8')
