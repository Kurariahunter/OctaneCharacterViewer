from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import html,math,shutil
R=Path('F:/DisneyInfinityPortalTest/ElsaSceneResearch')
W,H=1960,1580
im=Image.new('RGB',(W,H),'#f6f8fc');d=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#f6f8fc"/>']
fontroot=Path('C:/Windows/Fonts')
def font(size,bold=False):return ImageFont.truetype(str(fontroot/('arialbd.ttf' if bold else 'arial.ttf')),size)
def text(x,y,s,size=25,color='#17283f',bold=False):
 d.text((x,y),s,font=font(size,bold),fill=color)
 svg.append(f'<text x="{x}" y="{y+size*.94}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}">{html.escape(s)}</text>')
def box(x,y,w,h,fill,stroke='#bcc9d9'):
 d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=fill,outline=stroke,width=2)
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def arrow(points,color='#526885'):
 d.line(points,fill=color,width=3)
 svg.append('<polyline points="'+' '.join(f'{x},{y}'for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
 x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px);tri=[(x,y),(x-13*math.cos(a-.45),y-13*math.sin(a-.45)),(x-13*math.cos(a+.45),y-13*math.sin(a+.45))];d.polygon(tri,fill=color);svg.append('<polygon points="'+' '.join(f'{xx},{yy}'for xx,yy in tri)+f'" fill="{color}"/>')
def lines(x,y,items,size=24,gap=36):
 for i,s in enumerate(items):text(x,y+i*gap,s,size)
text(60,38,'Reading a PC ClipDataBlock',49,bold=True)
text(60,105,'Disney Infinity 3.0  |  verified Elsa PC variant  |  little-endian  |  schematic, not to scale',25,color='#526885')
text(60,174,'1  BYTE LAYOUT',28,bold=True)
text(625,174,'2  DECODE THE CONTENTS',28,bold=True)
text(1285,174,'3  RESOLVE AND EVALUATE',28,bold=True)
x=60;w=445
rows=[('HEADER  •  12 bytes',['+0x00  raw field (not assigned here)','+0x04  duration: float32','+0x08  flag: uint16 = 1','+0x0A  curve count N: uint16'],185,'#e1ebff'),('OFFSET TABLE  •  N + 2 uint32',['+0x0C  offsets[0] → float pool','offsets[1] → register / command block','offsets[2..N+1] → N curve blocks'],150,'#e1ebff'),('REGISTER / COMMAND BLOCK',['Register header + curve order','Timed commands, then static commands'],118,'#fff0ce'),('CURVE 0',['Header • metadata • knots • coefficients'],93,'#dff2e8'),('CURVE 1  …  CURVE N−1',['Same structure; variable sizes'],93,'#dff2e8'),('FLOAT POOL',['float32 constants; extends to block end'],93,'#f0e3fb')]
y=225
for title,body,h,c in rows:
 box(x,y,w,h,c);text(x+18,y+14,title,24,bold=True);lines(x+18,y+54,body,21,29);y+=h+14
text(65,y+8,'All offsets are relative to ClipDataBlock byte 0.',21,color='#526885')
# Commands expanded
box(625,225,580,365,'#fff9eb');text(647,244,'REGISTER + COMMAND TABLES',25,bold=True)
lines(647,290,['uint16 register count; uint16 curve count','uint16 curve-order entries (N values)','Timed header: byte extent + command count','Packed command words, then descriptors','Static count + words, then descriptors'],23,37)
box(647,490,535,76,'#ffe1a0');text(663,500,'16-bit packed command word',22,bold=True)
text(663,534,'[ descriptor count: 3 bits ][ target port: 13 bits ]',21)
arrow([(505,654),(560,654),(560,405),(625,405)])
# curves
box(625,625,580,470,'#ebf8f0');text(647,644,'ONE CURVE BLOCK',25,bold=True)
lines(647,691,['+0x00  uint16 kind: dimensions + low flags','+0x02  uint16 size field: segment count × 16','+0x04 / +0x08  float32 start / end time','+0x0C  4 float32 metadata per component','Then: uint16 segment-start knots','Then: 4 int16 coefficients per segment/component','Then: padding to the next 4-byte boundary'],22,37)
box(647,970,535,101,'#cbe9d6');lines(663,985,['Reconstruct coefficients with bias / scale.','Quantize sample time → choose segment','→ evaluate component values.'],22,28)
arrow([(505,773),(570,773),(570,850),(625,850)])
# resolve column
box(1285,225,610,365,'#eef2ff');text(1307,244,'COMMAND OPERANDS',25,bold=True)
lines(1307,291,['Timed scalar → scalar register','Register → curve index + component','Rotation descriptor → 3 operand selectors','Each selector chooses register or float pool','Static descriptor → opcode + float-pool index'],23,38)
box(1307,501,565,65,'#dde5ff');text(1323,514,'Result: typed channels keyed by source port',23,bold=True)
arrow([(1205,405),(1285,405)])
box(1285,625,610,470,'#f0e9fb');text(1307,644,'PORT → CONTROL → FINAL BONE',25,bold=True)
lines(1307,692,['port ↔ local index (check both directions)','local-used slot → ConnectionMapUsedDataNodes','→ source DataNode + readable control path','Apply constants / animated components','Evaluate graph: relationships, IK, transforms,','persistent dress dynamics and Aim feedback','→ skin-world transforms / native matrices'],23,42)
text(1307,1015,'Unmapped ports and unsupported operators',23,bold=True)
text(1307,1050,'remain explicit; do not guess a target.',23)
arrow([(1590,590),(1590,625)])
arrow([(1205,1010),(1245,1010),(1245,590),(1470,590),(1470,565)])
# key register inset
box(60,1160,1145,177,'#ffffff');text(82,1177,'REGISTER EXAMPLE  (logical relationship, not a byte offset)',24,bold=True)
lines(82,1220,['Curve 0: 3 components → registers 0, 1, 2     |     Curve 1: 1 component → register 3','A timed command references a register; the command’s port identifies its control.','A curve is not automatically a bone, and one curve can contain several components.'],23,34)
box(1285,1160,610,177,'#e0f0f7');text(1307,1177,'UNITY EXPORT',25,bold=True)
lines(1307,1223,['Convert basis → position / quaternion / scale','Bake Transform curves into AnimationClip','Validate matrices, skinning and saved playback.'],23,35)
arrow([(1590,1095),(1590,1160)])
box(60,1380,1835,135,'#fff0e7');text(82,1396,'SCOPE AND STATIC-ONLY EXCEPTION',24,bold=True)
lines(82,1436,['This diagram describes the supported animated PC layout, not every platform or motion format.','The tested lean clip has N = 0: no curve blocks or timed descriptors; its static commands and float pool still supply control values.'],23,34)
svg.append('</svg>')
(R/'PC_ClipDataBlock_Diagram.svg').write_text('\n'.join(svg),encoding='utf8');im.save(R/'PC_ClipDataBlock_Diagram.png')
mirror=Path('C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch')
for n in ['PC_ClipDataBlock_Diagram.svg','PC_ClipDataBlock_Diagram.png']:shutil.copy2(R/n,mirror/n)
print('Created PNG and editable SVG')
