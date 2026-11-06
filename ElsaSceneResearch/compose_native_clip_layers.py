"""Compose decoded channel records through the verified 52-byte native buffer blend.

Null filters and explicit weights/modes only. Port order is shared by all layers;
no runtime controller selection or initializer semantics are inferred here.
"""
import struct,math
from native_pc_raw_buffer_blend import replay

FIELDS={0:(4,3,0x0e),1:(4,1,2),2:(8,1,4),3:(12,1,8),
        4:(32,4,0x100),5:(16,3,0x70),6:(16,1,0x10),
        7:(20,1,0x20),8:(24,1,0x40),9:(28,1,0x80),10:(0,1,1)}

def compose(layers):
    ports=sorted({p for records,weight,mode in layers for p in records})
    if not ports or len(ports)>256:raise ValueError('Unsupported port extent')
    slots={p:i for i,p in enumerate(ports)}
    # Captured empty native rows have unit scales and an identity quaternion.
    neutral=struct.pack('<12fI',0,0,0,0,1,1,1,1,0,0,0,1,0)
    output=neutral*len(ports);identities={}
    for records,weight,mode in layers:
        source=bytearray(neutral*len(ports))
        for port,record in records.items():
            identity=(record['source_node'],record.get('path'))
            if port in identities and identities[port]!=identity:raise ValueError('Inconsistent port binding')
            identities[port]=identity;offset=slots[port]*52;mask=0
            for op,values in record['channels'].items():
                pos,count,bits=FIELDS[int(op)]
                if len(values)!=count:raise ValueError('Unexpected channel width')
                struct.pack_into('<'+'f'*count,source,offset+pos,*values);mask|=bits
            struct.pack_into('<I',source,offset+48,mask)
        output=replay(output,bytes(source),weight,mode)
    result={}
    for port,i in slots.items():
        offset=i*52;mask=struct.unpack_from('<I',output,offset+48)[0];channels={}
        if not all(math.isfinite(v)for v in struct.unpack_from('<12f',output,offset)):raise ValueError('Nonfinite native composed row at port '+str(port))
        # Decode component masks individually so partial channels remain partial.
        for op in (10,1,2,3,6,7,8,9,4):
            pos,count,bit=FIELDS[op]
            if mask&bit:channels[str(op)]=list(struct.unpack_from('<'+'f'*count,output,offset+pos))
        if mask&0x70==0x70:
            channels['5']=[channels.pop(str(op))[0]for op in (6,7,8)]
        node,path=identities[port]
        result[port]=dict(source_node=node,path=path,channels=channels)
    return result
