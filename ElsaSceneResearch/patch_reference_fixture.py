from pathlib import Path
p=Path('validate_dress_reference_native.py');s=p.read_text();s=s.replace('import json,random','import json,random,inspect,struct\nimport validate_foot_basis_native as fixture')
s=s.replace("rng=random.Random", "# Mixed normal/inverse chain stores the normal-input count at processor+0x1c.\ncode=inspect.getsource(fixture.native).replace('def native(', 'def reference_native(').replace('try:u.emu_start', \"if name=='ConcatenateChainInverseDilation':u.mem_write(proc+0x1c,struct.pack('<I',1))\\n try:u.emu_start\")\nnamespace=dict(vars(fixture));exec(code,namespace);native=namespace['reference_native']\nrng=random.Random")
p.write_text(s)
