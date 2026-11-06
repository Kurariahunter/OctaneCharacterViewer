# PC dress: consecutive captured update replay

2026-10-17. This extends the captured one-step test; it does not change Unity assets.

## Method

`replay_pc_dress_sequences.py` uses the hash-pinned installed PC executable in Unicorn and the existing 20261017_173236 capture. It partitions each connected dress chain into maximal consecutive runs. Both snapshots must have unchanged read-window stamps; global frame and chain last-frame stamps must each advance by exactly one. Gaps, repeated frames and changed read windows split runs. Missing samples never get interpolated.

The first transition of each run uses the existing numeric-state seed. Every later transition retains native particle state, output positions, velocities, last target, cached scalar and last-frame state from the previous emulated call. These are never corrected from the next captured snapshot. All pointers and metadata remain synthetic. Captured external dt/force, chain parameters, anchor/container transforms, root constraint and orientation feedback are still supplied each step. Thus this isolates continuity of the chain solver, not a closed-loop reconstruction of the upstream graph or final Aim/skin transforms.

## Results

- Left: 61 transitions in 50 runs; 9 multi-step runs.
- Right: 54 transitions in 43 runs; 9 multi-step runs.
- Total: 115 transitions, including 22 genuinely carried-state steps after their run's seed transition.
- All 22 carried-state steps match captured root/tip positions and velocity components exactly numerically. Maximum errors are 0.
- Longest run: 3 updates, approximately 0.041 seconds. This is short continuity evidence, not a seconds-long stability test.
- Both previous- and current-snapshot orientation variants match. Orientation feedback timing remains unresolved by these samples.
- Zero-force control matches none of the 22 carried-state steps; maximum tip error across all transitions is 0.0009764536456072611, maximum velocity component error 0.044345855712890625.

Report: `pc-captured-dress-sequence-replay.json`, including per-step predictions, observations, elapsed times and capture SHA256. The script fails on baseline mismatch or a missing multi-step evidence set and reports a separate zero-force control. No live process access occurs.

## Recording and next evidence

Movie_020 sampled frames show stable feet and no obvious recurrence of the earlier shin-through-front-hem gap. The passive dress remains broad and visually stiff. The preview's stationary ending is its intentionally held final pose. This visual observation is separate from the exact native state comparison.

The current capture cannot support longer replay runs because of frame gaps. A separate `Capture Dense Dress Sequence.cmd` requests 5ms sampling and only one upstream/IK context snapshot. This may provide longer consecutive runs but cannot guarantee them: process reads are non-atomic and Windows scheduling can skip frames. It preserves the existing standard command. Keep Elsa animating without changing scenes while it runs. The next analysis should discover connected chain addresses in the new capture and verify identity before replay; this replay script currently pins the existing capture and chain addresses.

Then compare downstream Aim/skin outputs against live context. Captured orientation remains an external input in this test, and no claim of complete animation decoding follows from these short runs.
