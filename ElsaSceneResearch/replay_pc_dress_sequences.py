"""Carry native particle state across maximal consecutive captured frame runs.

Only the first transition is seeded with captured particle state. Later steps
receive captured external inputs and orientation feedback, never captured
positions, velocities, last target, cached scale, or native last-frame state.
This tests the chain integrator, not an independently decoded upstream graph.
"""
import json
import struct
import hashlib
import argparse
from pathlib import Path
from replay_pc_dress_capture import replay, payload, CAPTURE, sha, u, BASE, PROC, invoke, positions
import numpy as np

R = Path(__file__).parent
CHAINS = [('0x1e07fdd0', 'Left'), ('0x1e07fe74', 'Right')]


def eligible(a, b, completed_only=False):
    if not a or not b or not a.get('dynamics') or not b.get('dynamics'):
        return False
    wa, wb = (c['dynamics']['read_window'] for c in (a, b))
    if completed_only and any(w['frame_before'] != w['last_frame_before'] for w in (wa, wb)):
        return False
    return (wa['stamps_changed'] is False and wb['stamps_changed'] is False
            and wb['frame_before'] - wa['frame_before'] == 1
            and wb['last_frame_before'] - wa['last_frame_before'] == 1)


def runs(frames, completed_only=False):
    """Return disjoint maximal chains of eligible transitions, including singles."""
    current = []
    for i in range(1, len(frames)):
        if eligible(frames[i-1], frames[i], completed_only):
            current.append(i)
        elif current:
            yield current
            current = []
    if current:
        yield current


def advance(a, b, orientation, zero_force, feedback_quaternion=None):
    da, db = a['dynamics'], b['dynamics']
    sb = {v['runtime_slot']: v for v in db['input_states']}
    if db['capsules']['count'] != 0 or any(bytes.fromhex(sb[8].get('payload_hex') or '')):
        raise ValueError('unsupported collision/reset input')
    ins = [BASE + 0x4000 + 256*i for i in range(19)]
    outs = [BASE + 0x4000 + 256*i for i in (19, 20)]
    # Preserve all integrator state from the previous native invocation.
    previous_native_frame = struct.unpack('<I', u.mem_read(ins[2]+0x34, 4))[0]
    if previous_native_frame != da['read_window']['last_frame_before']:
        raise ValueError('native frame continuity lost')
    for slot in (1, 3, 4, 5, 6, 11):
        payload(sb[slot])  # finite-value validation
        u.mem_write(ins[slot]+0x34, bytes.fromhex(sb[slot]['payload_hex']))
    if zero_force:
        u.mem_write(ins[3]+0x34, struct.pack('<3f', 0, 0, 0))
    q = (payload((da if orientation == 'previous' else db)['cached_orientation']['value'])
         if feedback_quaternion is None else list(feedback_quaternion))
    if len(q) != 4 or not all(np.isfinite(v) for v in q):
        raise ValueError('invalid orientation feedback')
    u.mem_write(BASE+0x4000+21*256+0x34, struct.pack('<4f', *q))
    u.mem_write(ins[0]+0x34, struct.pack('<I', db['read_window']['frame_before']))
    # Other native math adapters share this emulator and may clear these tags.
    for address, value in [(0x21aee78,1),(0x21aee7c,0xffffffff),
                           (0x213e48c,2),(0x213e490,0xffffffff),
                           (0x21ae4c8,3),(0x21ae4cc,0xffffffff)]:
        u.mem_write(address, struct.pack('<I', value))
    invoke(0x4ae360)
    predicted = np.array(positions(outs))
    expected = np.array([payload(v) for v in db['output_states']])
    velocity = np.array([struct.unpack('<3f', u.mem_read(ins[s]+0x34, 12)) for s in (12, 17)])
    wanted = np.array([payload(sb[s]) for s in (12, 17)])
    if not np.isfinite(predicted).all() or not np.isfinite(velocity).all():
        raise ValueError('nonfinite result')
    error = np.linalg.norm(predicted-expected, axis=1)
    native_frame = struct.unpack('<I', u.mem_read(ins[2]+0x34, 4))[0]
    if native_frame != db['read_window']['last_frame_before']:
        raise ValueError('native frame did not advance')
    return dict(root_error=float(error[0]), tip_error=float(error[1]),
                velocity_component_error=float(np.max(abs(velocity-wanted))),
                predicted=predicted.tolist(), expected=expected.tolist(), dt=payload(sb[1])[0])


def main(completed_only=False):
    data = json.loads(CAPTURE.read_text())
    if data['identity']['sha256'] != sha:
        raise ValueError('capture/executable mismatch')
    rows, coverage = [], []
    for address, side in CHAINS:
        frames = [next((c for c in s['chains'] if c and c['address'] == address), None)
                  for s in data['samples']]
        segments = list(runs(frames, completed_only))
        coverage.append(dict(chain=address, runs=len(segments),
            transitions=sum(map(len, segments)), multi_step_runs=sum(len(s)>1 for s in segments),
            longest_run_steps=max(map(len, segments), default=0)))
        for orientation, zero in [('previous', False), ('current', False), ('previous', True)]:
            for number, segment in enumerate(segments):
                elapsed = 0.0
                for step, index in enumerate(segment):
                    a, b = frames[index-1], frames[index]
                    result = (replay(a, b, side, orientation=orientation, zero_force=zero)
                              if step == 0 else advance(a, b, orientation, zero))
                    elapsed += result['dt']
                    rows.append(dict(chain=address, run=number, step=step+1,
                        sample_index=index, orientation=orientation, zero_force=zero,
                        elapsed_seconds=elapsed, **result))
    summaries = []
    for orientation, zero in [('previous', False), ('current', False), ('previous', True)]:
        group = [r for r in rows if (r['orientation'], r['zero_force']) == (orientation, zero)]
        carried = [r for r in group if r['step'] > 1]
        if not carried:
            raise ValueError('capture contains no multi-step evidence')
        summaries.append(dict(orientation=orientation, zero_force=zero, steps=len(group),
            carried_state_steps=len(carried),
            longest_run_seconds=max(r['elapsed_seconds'] for r in group),
            max_root_error=max(r['root_error'] for r in group),
            max_tip_error=max(r['tip_error'] for r in group),
            max_velocity_component_error=max(r['velocity_component_error'] for r in group),
            exact_carried_steps=sum(r['root_error']==r['tip_error']==r['velocity_component_error']==0 for r in carried)))
    baseline = summaries[0]
    passed = all(baseline[k] == 0 for k in ('max_root_error', 'max_tip_error', 'max_velocity_component_error'))
    if summaries[-1]['exact_carried_steps'] != 0:
        raise ValueError('zero-force control unexpectedly matches carried state')
    report = dict(capture=str(CAPTURE), capture_sha256=hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
        exe_sha256=sha, completed_snapshots_only=completed_only,
        exact_sequence_match=passed, coverage=coverage, summary=summaries,
        scope='Native chain state persists after the first seeded transition in each maximal run. External force, dt, chain data, anchor, container, root constraint and cached orientation remain capture-driven. No carried particle state is corrected between steps. Non-atomic capture; short runs only; not a final Aim/skin or full graph validation.', rows=rows)
    (R/'pc-captured-dress-sequence-replay.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(exact_sequence_match=passed, coverage=coverage, summary=summaries), indent=2))
    if not passed:
        raise SystemExit('Sequence mismatch recorded; do not claim equivalence.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, default=CAPTURE)
    parser.add_argument('--output-dir', type=Path, default=R)
    parser.add_argument('--completed-only', action='store_true',
        help='Require native last-frame equal global frame in both snapshots; unchanged stamps alone permit pending evaluations')
    args = parser.parse_args()
    CAPTURE = args.capture.resolve()
    R = args.output_dir.resolve()
    R.mkdir(parents=True, exist_ok=True)
    main(args.completed_only)
