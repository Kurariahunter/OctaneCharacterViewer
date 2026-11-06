"""Apply decoded PC clip leaf fields without replacing computed graph outputs."""
import copy
from evaluate_pc_arms import DN,PROD,get

def apply(e,records,allow_transform_scale=False):
 for record in records.values():
  node=record['source_node']
  if node is None or node in PROD:continue
  fields={c['name']:copy.deepcopy(c['value'])for c in next((c for c in DN[node]['children']if c['name']=='Data'),{'children':[]})['children']};ch=record['channels']
  if '0'in ch:fields['Translation']=ch['0'][:]
  for op in [1,2,3]:
   if str(op)in ch:fields.setdefault('Translation',[0,0,0])[op-1]=ch[str(op)][0]
  if '4'in ch:fields['Orientation']=ch['4'][:]
  if '10'in ch:fields['Value']=ch['10'][0]
  if allow_transform_scale and '5' in ch:
   if node not in (644,650) or get(DN[node],'Type')!='Transform' or len(ch['5'])!=3:raise ValueError('unverified scaled control')
   fields['Scale']=ch['5'][:]+[fields.get('Scale',[1]*4)[3]]
  partial_scale=allow_transform_scale and node in (644,650) and get(DN[node],'Type')=='Transform'
  if partial_scale:
   for op in (6,7,8):
    if str(op)in ch:
     if len(ch[str(op)])!=1:raise ValueError('Unexpected scale component width')
     fields.setdefault('Scale',[1]*4)[op-6]=ch[str(op)][0]
  for op in [5,6,7,8,9]:
   if str(op)in ch and not(allow_transform_scale and op==5) and not(partial_scale and op in (6,7,8)) and max(abs(v-1)for v in ch[str(op)])>1e-5:raise ValueError('unsupported nonunit control scale')
  e.overrides[node]=fields
