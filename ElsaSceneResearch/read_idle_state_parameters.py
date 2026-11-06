"""Read shared idle state parameters and character-specific BENT file aliases."""
import argparse,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
P='{Properties}'
def identifier(text):
 value=0
 for byte in text.encode('ascii'):value=(value*33+byte)&0xffffffff
 return value
def read(xml,bent):
 raw=Path(xml).read_bytes();root=ET.fromstring(raw);records=json.loads(Path(bent).read_text())['records'];aliases={}
 for i,r in enumerate(records):
  if r['name']!='File':continue
  for child in records[i+1:]:
   if child['depth']<=r['depth']:break
   if child['name']=='Filename':aliases[r['value']]=child['value'];break
 states=[]
 def visit(node,path):
  path=path+([node.attrib['name']]if 'name'in node.attrib else [])
  if node.tag=='AnimTreeState':
   fields={c.tag[len(P):]:c.attrib['value']for c in node if c.tag.startswith(P)and'value'in c.attrib}
   alias=fields.get('Clip','')
   if alias in ('IDLE_BREAKA','IDLE_BREAKB','IDLE_BREAKC'):
    states.append(dict(state_path='/'.join(path),clip_alias=alias,identifier=hex(identifier(alias)),ease_duration_units=float(fields['EaseDuration']),motion=aliases.get(alias),fields=fields))
  for child in node:visit(child,path)
 visit(root,[])
 return dict(xml=str(Path(xml).resolve()),xml_sha256=hashlib.sha256(raw).hexdigest(),bent_alias_input=str(Path(bent).resolve()),states=states,scope='XML state candidates and decoded BENT alias associations. Duplicate/shared states are retained. Runtime selection of a particular XML path and complete event scheduling are not established.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('xml');p.add_argument('bent');p.add_argument('--output',required=True);a=p.parse_args();r=read(a.xml,a.bent);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(dict(states=len(r['states']),aliases=sorted({s['clip_alias']for s in r['states']}))))
