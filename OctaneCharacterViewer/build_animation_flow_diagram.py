"""Editable SVG plus matching PNG of the evidence-bounded animation dataflow."""
from pathlib import Path
from html import escape
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent/'Diagrams';R.mkdir(exist_ok=True)
W,H=1200,1920
im=Image.new('RGB',(W,H),'#fcfcfa');d=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">', '<title id="title">Disney Infinity animation: file to game</title>','<desc id="desc">Research diagram separating verified PC Elsa animation stages, bounded runtime behavior and the unresolved runtime render binding from the standalone viewer route.</desc>',f'<rect width="{W}" height="{H}" fill="#fcfcfa"/>']
colors={'green':('#e1f5ee','#0f6e56','#085041'),'amber':('#fff3d6','#a66c13','#704809'),'red':('#fdebea','#b54d4b','#873432'),'blue':('#eaf1fc','#486da3','#274e80')}
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
def text(x,y,s,size=19,color='#26343d',bold=False,center=True):
 d.text((x,y),s,font=font(size,bold),fill=color,anchor='mm' if center else 'lm')
 svg.append(f'<text x="{x}" y="{y}" text-anchor="{"middle" if center else "start"}" dominant-baseline="central" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{600 if bold else 400}" fill="{color}">{escape(s)}</text>')
def box(x,y,w,h,title,lines,kind='green',badge=None):
 bg,stroke,fg=colors[kind];d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=bg,outline=stroke,width=2)
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{bg}" stroke="{stroke}" stroke-width="1.5"/>')
 text(x+w/2,y+28,title,23,fg,True)
 for i,line in enumerate(lines):text(x+w/2,y+59+i*25,line,18,fg)
 if badge:text(x+w-12,y+h-16,badge,13,fg,False,False)
def arrow(points,dashed=False):
 color='#86929b'
 if not dashed:d.line(points,fill=color,width=2)
 else:
  for (x1,y1),(x2,y2) in zip(points,points[1:]):
   length=((x2-x1)**2+(y2-y1)**2)**.5
   for z in range(0,int(length),12):
    a=z/length;b=min(z+6,length)/length;d.line((x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b),fill=color,width=2)
 x,y=points[-1];px,py=points[-2]
 if y>py:head=[(x,y),(x-5,y-8),(x+5,y-8)]
 elif x>px:head=[(x,y),(x-8,y-5),(x-8,y+5)]
 else:head=[(x,y),(x+8,y-5),(x+8,y+5)]
 d.polygon(head,fill=color)
 p=' '.join(f'{a},{b}'for a,b in points);dash=' stroke-dasharray="6 6"'if dashed else ''
 svg.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="2"{dash}/><polygon points="'+ ' '.join(f'{a},{b}'for a,b in head)+f'" fill="{color}"/>')
text(600,44,'Disney Infinity animation: file to game',34,'#20343a',True)
text(600,84,'Our current understanding | PC Gold Edition / Elsa | 22 October 2026',19,'#607078')
for x,kind,label in ((62,'green','Verified (bounded tests)'),(360,'amber','Partial / fixture'),(650,'red','Unresolved link'),(940,'blue','Asset / output')):
 bg,st,fg=colors[kind];d.rounded_rectangle((x,117,x+18,135),radius=4,fill=bg,outline=st);svg.append(f'<rect x="{x}" y="117" width="18" height="18" rx="4" fill="{bg}" stroke="{st}"/>');text(x+28,126,label,17,fg,center=False)
box(40,166,350,130,'Motion assets',['Game archives -> extracted files','Motion .oct: ClipDataBlock','Packed curve / channel records'],'blue')
box(425,166,350,130,'Character configuration',['BENT motion aliases + animtree','State paths, overrides, parameters','Example: IDLE_BREAKC -> specific03'],'blue')
box(810,166,350,130,'Rig + mesh assets',['Rig .oct: ports and processor graph','Skin influences and inverse binds','VBUF / IBUF: geometry and weights'],'blue')
for x in (215,600,985):arrow([(x,296),(x,318),(600,318),(600,342)])
box(190,342,820,104,'1  Load and interpret the authored data',['Resolve motion aliases, rig definitions and compressed curve blocks','File structures decoded; this is not a complete game-loader reconstruction'],'green')
arrow([(600,446),(600,476)])
box(190,476,820,122,'2  Choose motion, advance time, activate a transition',['State / action chooses a clip or layer group; clocks select curve time','Native duration selection and selected clock/fade paths verified','Automatic gameplay scheduling and default policies remain incomplete'],'amber')
arrow([(600,598),(600,628)])
box(190,628,820,122,'3  Sample curves and resolve their target ports',['Decode scalar, translation, rotation and scale channel values','Port / connection maps bind source channels to rig controls','A port index is not a mesh bone index'],'green')
arrow([(600,750),(600,780)])
box(190,780,820,122,'4  Blend channel controls',['Native Float, Dilation and Transform operations; filters / weights','Run group: main + upper-body + lean, in verified source order','Selected native operations verified; no universal runtime layer scheduler'],'green')
arrow([(600,902),(600,932)])
box(190,932,820,122,'5  Evaluate the character rig graph',['Connections, relationships, IK, aims and transform composition','Controls become bone / helper transforms, including face and fingers','Latest capture: six coherent hand snapshots replay with zero error'],'green')
arrow([(600,1054),(600,1084)])
box(190,1084,820,122,'6  Resolve world transforms and secondary motion',['Native scale compensation; chronological braid / dress feedback','Individual math and bounded chains verified; scene context is incomplete','Gravity, reset state, collision and timing must match the actor context'],'amber')
arrow([(600,1206),(600,1230),(320,1230),(320,1272)],True)
arrow([(600,1206),(600,1230),(880,1230),(880,1272)])
text(320,1252,'ORIGINAL GAME',17,'#704809',True)
text(880,1252,'OUR RECONSTRUCTION',17,'#274e80',True)
box(40,1272,560,150,'7A  Runtime render / skin binding',['Load capture found a 62-slot mesh table,','but its matrices remain at zero stamps.','Moving hand outputs use different addresses.','Runtime copy / remap / consumer link is unresolved.'],'red')
box(640,1272,520,150,'7B  Bake an evaluated palette',['Known rig skin outputs -> world matrices','62 / 62 source-evaluated palette bones','Saved samples, explicit preview state / timing','Tested Elsa idles + selected locomotion'],'green')
arrow([(320,1422),(320,1462)],True);arrow([(900,1422),(900,1462)])
box(40,1462,560,146,'8A  Native game skinning + draw',['Runtime palette + inverse binds + vertex weights','Deform mesh, shade, render the character','Exact moving palette-to-renderer path still unverified','This is not evidence of a broken game renderer.'],'amber')
box(640,1462,520,146,'8B  Standalone preview / Unity route',['Sample cache + mesh + binds + weights','WPF viewer skins the verified PC Elsa mesh','Unity route: world -> local -> AnimationClip curves','Latest full-palette bakes are viewer artifacts.'],'blue')
box(40,1652,1120,130,'How to read this diagram',['Solid arrows show the understood data dependency, not a complete native call trace.','Rig evaluation includes feedback; it is not necessarily one linear pass through these boxes.','62 / 62 palette coverage does not prove full engine or game-rendering parity.'],'blue')
text(600,1802,'Current research target: link the moving actor graph to its actual runtime skinning inputs.',21,'#873432',True)
text(600,1844,'Evidence: full-palette audits, native operator tests, live hand replay and scene-binding capture.',18,'#607078')
text(600,1875,'Cross-platform PS4 / Wii U references support research; this validated path is PC-specific.',18,'#607078')
svg.append('</svg>');(R/'disney_infinity_animation_file_to_game.svg').write_text('\n'.join(svg),encoding='utf-8');im.save(R/'disney_infinity_animation_file_to_game.png')
print(str(R.resolve()))
