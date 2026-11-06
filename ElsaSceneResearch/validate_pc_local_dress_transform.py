"""Captured root/anchor -> native inverse point -> native local dress compose."""
import json, hashlib, argparse
from pathlib import Path
from native_pc_dress_math import inverse_point, sha
from native_pc_transform_scale import compose, point
from native_pc_dress_math import call
from native_pc_skin_matrix import matrix

R=Path(__file__).parent
CAPTURE=R.parent/'OctaneLiveInspector/Captures/octane_20261017_181340_1792275220781381600.json'


def main(output_dir=None):
    data=json.loads(CAPTURE.read_text())
    if data['identity']['sha256']!=sha:
        raise ValueError('capture/executable mismatch')
    rows=[];excluded={}
    for index,sample in enumerate(data['samples']):
        for row in sample.get('dress_skin',[]):
            if row['chain']not in ('0x1e07fdd0','0x1e07fe74'):
                continue
            if row['errors']or not row.get('read_window',{}).get('completed_frame'):
                excluded[row['chain']]=excluded.get(row['chain'],0)+1
                continue
            n=row['nodes']
            root=n['particle_position_0']['floats'];anchor=n['anchor']['floats']
            q=n['orientation']['floats'];wanted=n['local_transform']['floats']
            if n['component_scale']is not None or n['component_unscale']is not None:
                raise ValueError('unsupported authored component overrides')
            # Source local compose has only Translation/Orientation inputs, unit
            # stored Scale4/Unscale4. No captured aggregate used to fit prediction.
            translation=inverse_point(root,anchor)
            predicted=compose(q,translation,[1]*4,[1]*4)
            component_predicted=compose(q,n['component_translation']['floats'],[1]*4,[1]*4)
            def error(a,b):return max(abs(x-y)for x,y in zip(a,b))
            rows.append(dict(chain=row['chain'],sample_index=index,
                global_frame=row['read_window']['frame_before'],
                matches_dynamics_frame=row['read_window']['matches_dynamics_frame'],
                predicted_local_transform=predicted,captured_local_transform=wanted,
                max_component_error=error(predicted,wanted),
                translation_error=error(translation,n['component_translation']['floats']),
                captured_component_compose_error=error(component_predicted,wanted)))
            if n.get('world_transform'):
                world=call(0x57e240,[predicted,anchor],'array',16)
                captured_local_world=call(0x57e240,[wanted,anchor],'array',16)
                world_wanted=n['world_transform']['floats']
                rows[-1].update(predicted_world_transform=world,captured_world_transform=world_wanted,
                    world_component_error=error(world,world_wanted),
                    captured_local_world_component_error=error(captured_local_world,world_wanted))
                _,consumed_world=point(world,[0,0,0],return_state=True)
                basis_errors=[error(point(world,v),point(world_wanted,v))for v in
                              ([0,0,0],[1,0,0],[0,1,0],[0,0,1],[.17,-.29,.43])]
                rows[-1].update(predicted_world_after_native_point=consumed_world,
                    world_after_native_point_component_error=error(consumed_world,world_wanted),
                    world_basis_point_error=max(basis_errors),
                    differing_raw_world_components=[i for i,(a,b)in enumerate(zip(world,world_wanted))if a!=b])
                if n.get('matrix_output'):
                    item=n['matrix_output']
                    if item.get('payload_offset')!=0x40 or len(item['floats'])!=12:
                        raise ValueError('unsupported live matrix layout')
                    predicted_matrix=matrix(world)
                    rows[-1].update(predicted_matrix=predicted_matrix,captured_matrix=item['floats'],
                        matrix_component_error=error(predicted_matrix,item['floats']),
                        captured_world_matrix_component_error=error(matrix(world_wanted),item['floats']))
    if not rows:raise ValueError('no completed local Transform samples')
    summary=dict(completed_samples=len(rows),excluded_samples=excluded,
        matching_dynamics_samples=sum(r['matches_dynamics_frame']for r in rows),
        max_component_error=max(r['max_component_error']for r in rows),
        max_translation_error=max(r['translation_error']for r in rows),
        max_captured_component_compose_error=max(r['captured_component_compose_error']for r in rows))
    world_rows=[r for r in rows if 'world_component_error'in r]
    if world_rows:
        summary.update(world_comparisons=len(world_rows),
            max_world_component_error=max(r['world_component_error']for r in world_rows),
            max_captured_local_world_component_error=max(r['captured_local_world_component_error']for r in world_rows),
            max_world_after_native_point_component_error=max(r['world_after_native_point_component_error']for r in world_rows),
            max_world_basis_point_error=max(r['world_basis_point_error']for r in world_rows))
    summary['distinct_chain_frame_pairs']=len({(r['chain'],r['global_frame'])for r in rows})
    matrix_rows=[r for r in rows if 'matrix_component_error'in r]
    if matrix_rows:
        summary.update(matrix_comparisons=len(matrix_rows),
            max_matrix_component_error=max(r['matrix_component_error']for r in matrix_rows),
            max_captured_world_matrix_component_error=max(r['captured_world_matrix_component_error']for r in matrix_rows))
    out=output_dir or R/'LocalDress181340';out.mkdir(parents=True,exist_ok=True)
    report=dict(capture=str(CAPTURE),capture_sha256=hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        exe_sha256=sha,summary=summary,rows=rows,
        scope='Native inverse captured anchor/root -> compose with captured local quaternion and source unit scales -> local payload. World concatenate combines predicted local with captured anchor. Raw comparison retained separately from native point-consumer materialization and five point comparisons. If present, packed12 matrix output at+40 is compared with original native55da50, from both predicted and captured world inputs. Captured quaternion isolates composition; this is not a closed-loop particle/Aim test. Completed snapshots are non-atomic and may repeat frames. Renderer palette consumption is not proven by a converter output alone.')
    (out/'pc-local-dress-transform-validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(summary,indent=2))
    if summary['max_component_error']!=0 or any(
        r['world_after_native_point_component_error']!=0 or r['world_basis_point_error']!=0
        or any(i!=11 for i in r['differing_raw_world_components'])for r in world_rows)or any(
            r['matrix_component_error']!=0 for r in matrix_rows):
        raise SystemExit('Transform mismatch retained in report')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,default=CAPTURE)
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args();CAPTURE=args.capture.resolve()
    main(args.output_dir)
