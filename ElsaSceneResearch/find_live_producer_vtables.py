from exe_reader import *
for name,fn in [('ConcatenateDilationTransform',0x57cb30),('ConcatenateTransformDilation',0x4d0c50),('ConcatenateChainTransform',0x57e240),('InvertTransform',0x4d1a60),('TransformComponentProcessorCompose',0x5303e0)]:
 off=0;vts=[]
 while True:
  off=b.find(struct.pack('<I',fn),off)
  if off<0:break
  v=next(base+r+off-p for r,s,p in sections if p<=off<p+s);off+=1
  if 0x1b00000<v<0x1c00000:vts.append(hex(v-64))
 print(name,hex(fn),vts)
