# Parent clock setup — 2026-10-19

Same PC EXE identity and preferred addresses as ENGINE_CLOCK_WRITER_HANDOFF.md. No viewer changes.

## Initializer evidence

Function 0x6787E0 calls the raw timer, then initializes parent clock fields. Tested window 0x6787F0..0x678844 writes raw/effective delta 17 ms (+4/+0x10), delta seconds float32(.017) at +0x1C, mode and prior mode 3 (+0x28/+0x2C), custom multiplier 1 (+0x44), zero accumulated times and zero one-shot/transition flags. The window does not write cap +0x34 or smoothing parameter +0x38; their live defaults remain unknown. Raw timer and optional logging are excluded from this window test.

## Transition setter evidence

Complete setter 0x6788C0 first translates the requested selection through 0x6781A0, then invokes 0x678860. With logging byte +0x52 clear, these are the only invoked routines besides the scale getters/configuration helpers.

0x678860 enables smoothing only when requested and abs(parent+0x38) exceeds epsilon. It obtains current scale through 0x678490, which reads the prior mode (+0x2C), or returns the already-smoothed current scale if a transition is active. It derives target scale from the newly selected mode (+0x28) and shift (+0x30), writes current/target at +0x3C/+0x40, and sets transition byte +0x51. Otherwise it clears that flag. It does not rewrite effective delta +0x10.

20 full-setter fixtures cover selections 0..9 with smoothing requested/off, prior normal mode, smoothing parameter .25, logging disabled, and effective delta 17 ms. All pass. Every requested transition starts with current scale 1 and the selected target scale, while effective delta remains 17 ms. Setter-disabled cases clear the transition flag. Zero/tiny smoothing parameter and interruption of an already-active transition were statically identified but are not covered by these fixtures.

Combined with the previous 32 transition-window and 30 full child-clock tests, this establishes retained effective delta across the tested setup/update path. It does not establish every parent-state writer or global runtime scheduling. Avoid replacing this behavior with invented delta*smoothedScale arithmetic.

## Next

Determine where cap/smoothing parameter are assigned and how update wrapper 0x133EE60 precedes or interleaves publication wrapper 0x6A0740. If live state capture is needed, include the complete 0x58-byte parent clock prefix and wrapper order, rather than requesting a longer undirected gameplay recording. The current evidence does not yet require a user capture.

Artifacts: validate_pc_clock_setup.py, clock-setup-validation.json, clock_setup.txt. Existing native viewer remains unchanged while scheduler assumptions are unresolved.
