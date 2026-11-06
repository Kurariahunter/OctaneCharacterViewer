"""Inspect a native PC clip using existing file/native curve decoders; no full-pose claim."""
import argparse, hashlib, json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'ElsaSceneResearch'))

def inspect(path):
    path=Path(path).resolve()
    if path.suffix.lower()!='.oct' or not path.is_file() or path.stat().st_size>32*1024*1024:
        raise ValueError('Choose an extracted native clip OCT smaller than 32 MiB.')
    from read_pc_idle_files import Rig, Clip
    rig=Rig(ROOT/'ElsaSceneResearch/InstalledGameAssetCheck/fro_elsa/fro_elsa.oct')
    clip=Clip(path,rig)
    if not math.isfinite(clip.duration) or not 0<clip.duration<=600:
        raise ValueError('Invalid or unsupported clip duration.')
    samples=[]
    for fraction in (0,.25,.5,.75,1):
        time=clip.duration*fraction
        channels=clip.sample(time)
        for row in channels.values():
            for values in row['channels'].values():
                if not all(math.isfinite(v) for v in values):raise ValueError('Nonfinite decoded channel')
        samples.append({'time':time,'ports':channels})
    ports=sorted({c['port'] for c in clip.layout['commands']+clip.constants['tracks']})
    return dict(schema='octane-native-clip-inspection-v1',source=str(path),
        source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),clipdata_sha256=clip.sha,
        model_sha256=rig.sha,duration=clip.duration,curve_count=len(clip.layout['curves']),
        dynamic_records=len(clip.layout['commands']),constant_records=len(clip.constants['tracks']),
        referenced_ports=len(ports),mapped_ports=len(set(ports)-set(clip.unmapped)),
        unmapped_ports=clip.unmapped,samples=samples,
        scope='Native scalar curve and Euler evaluation, five sample times; port mapping is against verified PC Elsa only. No full skin-palette evaluation, layer composition, dynamics, or arbitrary-character playback. Unsupported formats reject explicitly. The displayed preview is unchanged.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('clip');parser.add_argument('--output',required=True);args=parser.parse_args()
    report=inspect(args.clip);output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix(output.suffix+'.tmp');temp.write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8');temp.replace(output)
    print(json.dumps({k:v for k,v in report.items() if k!='samples'}))
if __name__=='__main__':main()
