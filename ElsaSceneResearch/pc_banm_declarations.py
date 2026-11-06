"""Bounded parser for the observed textual .banm declaration syntax. No execution."""
import re,math
TOKEN=re.compile(r'\s+|//[^\r\n]*|"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z_0-9]*|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|[{}\[\]=]')
def parse(text):
 if len(text)>2_000_000:raise ValueError('BANM size limit')
 tokens=[];offset=0
 for match in TOKEN.finditer(text):
  if match.start()!=offset:raise ValueError('unsupported token at '+str(offset))
  offset=match.end();value=match.group()
  if not value.isspace()and not value.startswith('//'):tokens.append((value,match.start()))
 if text[offset:].strip():raise ValueError('trailing unsupported text')
 if len(tokens)>100000:raise ValueError('BANM token limit')
 cursor=0
 def peek():return tokens[cursor][0]if cursor<len(tokens)else None
 def take(expected=None):
  nonlocal cursor
  if cursor>=len(tokens):raise ValueError('unexpected end')
  token=tokens[cursor];cursor+=1
  if expected is not None and token[0]!=expected:raise ValueError('expected '+expected)
  return token
 def scalar():
  value,_=take()
  if value.startswith('"'):
   # Preserve asset-path contents; reject escapes until their loader semantics are known.
   if '\\'in value:raise ValueError('unsupported string escape')
   return value[1:-1]
  try:number=float(value)
  except ValueError:raise ValueError('expected literal')
  if not math.isfinite(number):raise ValueError('nonfinite literal')
  return number
 def entries(depth=0,closing=None):
  if depth>64:raise ValueError('BANM depth limit')
  out=[]
  while peek()is not None and peek()!=closing:
   key,position=take()
   if not re.fullmatch('[A-Za-z_][A-Za-z_0-9]*',key):raise ValueError('expected field name')
   label=scalar()if peek()and peek().startswith('"')else None
   take('=');node={'field':key,'label':label,'line':text.count('\n',0,position)+1}
   if peek()=='{':take('{');node['children']=entries(depth+1,'}');take('}')
   elif peek()=='[':
    take('[');values=[]
    while peek()!=']':values.append(scalar())
    take(']');node['value']=values
   else:node['value']=scalar()
   out.append(node)
  return out
 result=entries()
 if cursor!=len(tokens):raise ValueError('unexpected closing token')
 return result

def descendants(nodes):
 for node in nodes:
  yield node
  yield from descendants(node.get('children',[]))
