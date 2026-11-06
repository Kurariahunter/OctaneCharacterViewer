"""Original PC TransformToMatrix variant: typed refs, aligned 12-float output."""
import struct
import math
from native_pc_transform_scale import u,execute,PROC,META


def matrix(raw):
    return _matrix(raw,16,0x55da50)


def dilation_matrix(raw):
    """RTTI-mapped Dilation3d -> XfrmTransMat; not a Transform reinterpretation."""
    return _matrix(raw,8,0x4dee10)


def _matrix(raw,width,fn):
    if len(raw)!=width or not all(math.isfinite(x)for x in raw):
        raise ValueError('unexpected matrix converter input')
    source=0x10004000;output=0x10004100
    u.mem_write(PROC,b'\0'*512);u.mem_write(META,b'\0'*64)
    for address in (source,output):
        u.mem_write(address,b'\0'*160)
        u.mem_write(address+0x10,struct.pack('<I',META))
        u.mem_write(address+0x1c,struct.pack('<I',META))
    u.mem_write(source+0x34,struct.pack('<'+'f'*width,*raw))
    u.mem_write(PROC+0x18,struct.pack('<2I',source,output))
    for address in (0x21aee78,0x21aee7c,0x213e710,0x213e70c,0x213e490,0x213e48c):
        u.mem_write(address,struct.pack('<I',0))
    execute(fn,[])
    result=list(struct.unpack('<12f',u.mem_read(output+0x40,48)))
    if not all(math.isfinite(x)for x in result):raise ValueError('nonfinite matrix result')
    return result
