import zipfile,hashlib
from pathlib import Path
for p in [Path('G:/Downloads/fro_elsa.zip'),Path('F:/Games/Disney Infinity - Gold Collection/Disney Infinity 3.0/assets/characters/fro_elsa/fro_elsa.zip')]:
 print(p)
 try:
  with zipfile.ZipFile(p) as z:
   print('entries',len(z.infolist()))
   for x in z.infolist():
    if x.filename.endswith('fro_elsa.oct') or 'idle_active.oct' in x.filename or 'idle_passive.oct' in x.filename:
     print(x.filename,x.file_size,x.compress_type,x.flag_bits)
     try:print('sha',hashlib.sha256(z.read(x)).hexdigest())
     except Exception as e:print(type(e).__name__,str(e))
 except Exception as e:print(type(e).__name__,str(e))
