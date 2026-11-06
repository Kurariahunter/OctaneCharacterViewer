"""Compare carried native particle predictions through PC source Aim to live rotors.

Consumes the retained replay report. No captured output quaternion is used as an
Aim initializer in the primary comparison; identity is the explicit initializer.
"""
import json, math, hashlib
from pathlib import Path
from validate_pc_dress_orientation import procs, dn, get, refs, angle
from native_pc_dress_math import aim, inverse_vector, difference, sha
from replay_pc_dress_sequences import runs, replay as seed_step, advance

R = Path(__file__).parent
REPORT = R/'DenseCapture175321/Completed/pc-captured-dress-sequence-replay.json'


def main():
    replay = json.loads(REPORT.read_text())
    capture_path = Path(replay['capture'])
    if hashlib.sha256(capture_path.read_bytes()).hexdigest() != replay['capture_sha256']:
        raise ValueError('capture/report hash mismatch')
    capture = json.loads(capture_path.read_text())
    if capture['identity']['sha256'] != sha or not replay['exact_sequence_match']:
        raise ValueError('invalid replay provenance')
    mappings = {}
    for address, pid in [('0x1e07fdd0', 550), ('0x1e07fe74', 551)]:
        dynamic = next(p for p in procs if int(p['value']) == pid)
        dr = refs(dynamic)
        inverse = next(p for p in procs if get(p, 'Type') == 'InverseTransformVectorWithTransform'
                       and refs(p)['Converter'] == dr['AnchorToWorld'])
        ir = refs(inverse)
        ap = next(p for p in procs if get(p, 'Type') == 'AimConstraintProcessorNode'
                  and refs(p)['AlignInput'] == ir['Output'])
        ar = refs(ap)
        diff = next(p for p in procs if get(p, 'Type') == 'Position3dDifferenceProcessor'
                    and refs(p)['Output'] == ir['Input'])
        fr = refs(diff)
        if fr['To'] != dr['Position[1]'] or fr['From'] != dr['Position[0]']:
            raise ValueError('source particle-to-Aim connectivity mismatch')
        if set(ar) != {'AlignInput','AlignReference','UpInput','UpReference','Output'}:
            raise ValueError('unexpected optional Aim inputs')
        constants = [get(dn[ar[k]], 'Data') for k in ('AlignReference','UpInput','UpReference')]
        if not all(isinstance(v, list) and len(v) == 3 for v in constants):
            raise ValueError('nonconstant Aim reference')
        mappings[address] = dict(dynamic=pid, inverse=int(inverse['value']),
            aim=int(ap['value']), output=ar['Output'], reference_vectors=constants)
    rows = []
    feedback = {}
    for row in replay['rows']:
        if row['orientation'] != 'previous' or row['zero_force']:
            continue
        chain = next(c for c in capture['samples'][row['sample_index']]['chains']
                     if c['address'] == row['chain'])
        d = chain['dynamics']
        states = {v['runtime_slot']: v for v in d['input_states']}
        import struct
        def unpack(item):
            raw = bytes.fromhex(item['payload_hex'])
            values = list(struct.unpack('<'+'f'*(len(raw)//4), raw))
            if not all(math.isfinite(v) for v in values):
                raise ValueError('nonfinite capture payload')
            return values
        anchor = unpack(states[5])
        wanted = unpack(d['cached_orientation']['value'])
        delta = difference(row['predicted'][1], row['predicted'][0])
        local = inverse_vector(delta, anchor)
        constants = mappings[row['chain']]['reference_vectors']
        q = aim(local, *constants, initial=[0,0,0,1])
        alternative = aim(local, *constants, initial=wanted)
        key = (row['chain'], row['run'])
        if row['step'] == 1:
            previous_chain = next(c for c in capture['samples'][row['sample_index']-1]['chains']
                                  if c['address'] == row['chain'])
            feedback[key] = unpack(previous_chain['dynamics']['cached_orientation']['value'])
        propagated = aim(local, *constants, initial=feedback[key])
        feedback[key] = propagated
        error = angle(q, wanted)
        rows.append(dict(chain=row['chain'], sample_index=row['sample_index'],
            step=row['step'], run=row['run'], predicted_quaternion=q,
            captured_quaternion=wanted, angular_error_degrees=error,
            propagated_quaternion=propagated,
            propagated_angular_error_degrees=angle(propagated, wanted),
            captured_initializer_error_degrees=angle(alternative, wanted),
            initializer_difference_degrees=angle(q, alternative),
            sign_invariant_component_error=min(max(abs(a-b) for a,b in zip(q,wanted)),
                                               max(abs(a+b) for a,b in zip(q,wanted)))))
    carried = [r for r in rows if r['step'] > 1]
    summary = dict(comparisons=len(rows), carried_state_comparisons=len(carried),
        max_angular_error_degrees=max(r['angular_error_degrees'] for r in rows),
        max_carried_angular_error_degrees=max(r['angular_error_degrees'] for r in carried),
        max_component_error=max(r['sign_invariant_component_error'] for r in rows),
        max_propagated_angular_error_degrees=max(r['propagated_angular_error_degrees'] for r in rows),
        max_carried_propagated_angular_error_degrees=max(r['propagated_angular_error_degrees'] for r in carried),
        max_captured_initializer_error_degrees=max(r['captured_initializer_error_degrees'] for r in rows),
        max_initializer_difference_degrees=max(r['initializer_difference_degrees'] for r in rows))
    closed_rows = []
    for address, mapping in mappings.items():
        frames = [next(c for c in s['chains'] if c['address'] == address) for s in capture['samples']]
        for run_number, segment in enumerate(runs(frames, completed_only=True)):
            orientation = unpack(frames[segment[0]-1]['dynamics']['cached_orientation']['value'])
            for step, index in enumerate(segment):
                a, b = frames[index-1], frames[index]
                result = (seed_step(a,b,'Left' if mapping['dynamic']==550 else 'Right') if step==0
                          else advance(a,b,'previous',False,feedback_quaternion=orientation))
                states = {v['runtime_slot']:v for v in b['dynamics']['input_states']}
                local = inverse_vector(difference(result['predicted'][1],result['predicted'][0]), unpack(states[5]))
                orientation = aim(local, *mapping['reference_vectors'], initial=orientation)
                wanted = unpack(b['dynamics']['cached_orientation']['value'])
                component_error = min(max(abs(x-y) for x,y in zip(orientation,wanted)),
                                      max(abs(x+y) for x,y in zip(orientation,wanted)))
                closed_rows.append(dict(chain=address, run=run_number, step=step+1, sample_index=index,
                    root_error=result['root_error'], tip_error=result['tip_error'],
                    velocity_component_error=result['velocity_component_error'],
                    quaternion_component_error=component_error,
                    angular_error_degrees=angle(orientation,wanted)))
    closed_summary = dict(steps=len(closed_rows), carried_steps=sum(r['step']>1 for r in closed_rows),
        **{'max_'+key:max(r[key] for r in closed_rows) for key in
           ('root_error','tip_error','velocity_component_error','quaternion_component_error','angular_error_degrees')})
    report = dict(capture=str(capture_path), capture_sha256=replay['capture_sha256'],
        exe_sha256=sha, mappings=mappings, summary=summary, rows=rows,
        closed_loop_summary=closed_summary, closed_loop_rows=closed_rows,
        scope='Native particle predictions -> difference -> inverse captured anchor Transform -> source-constant Aim -> captured cached local rotor. Primary identity initializer; separate propagated variant seeds orientation once per run. Closed-loop variant also feeds its own computed Aim back into the next native particle update; captured particle/rotation state seeds only the run start. External transforms/force/dt/root constraints remain capture-driven. Current captured quaternion initializer is diagnostic only. Final live skin matrices are absent from this capture schema. Non-atomic snapshots and short runs remain qualifications.')
    (REPORT.parent/'pc-sequence-aim-validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(aim=summary, closed_loop=closed_summary), indent=2))
    if any(closed_summary['max_'+key] > 1e-6 for key in
           ('root_error','tip_error','velocity_component_error','quaternion_component_error')):
        raise SystemExit('Closed-loop mismatch retained in report')


if __name__ == '__main__':
    main()
