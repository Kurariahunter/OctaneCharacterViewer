import zlib
for s in ['DefaultDataIndices','DefaultData','ConnectionMapUsedDataNodes']:
 print(s,hex(zlib.crc32(s.encode())),hex(zlib.crc32(s.lower().encode())))
