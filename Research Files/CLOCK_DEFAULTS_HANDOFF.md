# Clock defaults and scheduler limits — 2026-10-19

Same preferred addresses and hash-pinned EXE as earlier clock handoffs.

## Defaults now established

At 0x1AA4030 the static startup code loads ECX=0x22018F0 and calls constructor 0x67A930. Its field initialization window at 0x67A9C7..0x67A9FC writes:

| Owner field | Default |
|---|---|
| +0x34 | 100 ms cap |
| +0x38 | 0 smoothing parameter |
| +0x44 | float 1 custom multiplier |
| +0x48 / +0x4C | integer 30; semantics not established |
| +0x52 / +0x53 / +0x54 | zero bytes |

`validate_pc_clock_defaults.py` executes that original field window and asserts all these values. It also checks the singleton ECX instruction bytes in the startup caller. Container construction and subsequent reset are outside this fixture. Previous reset-window tests independently establish mode 3 and a 17 ms initial effective delta.

Default smoothing is disabled because parameter +0x38 is zero, even when requested through 0x6788C0. Earlier tests using .25 deliberately exercised an optional mode, not the startup default. Normal mode uses the capped integer delta directly, then converts accumulated uint32 milliseconds to seconds.

Absolute writes also show a runtime override: instruction 0x16AFC7F sets global 0x2201924 (owner+0x34) to 60 ms; 0x16AF18F restores it to 100 ms. Nearby code increments/decrements global 0x228B60C. Their broader feature identity is not established. Do not label this override as gameplay/rendering/physics-specific without further evidence.

## Scheduler status

0x1362190 is a verified function entry. In its successful polling branch, it repeatedly calls clock-update wrapper 0x133EE60 at 0x13621C2 until helper 0x1348F50 returns false. This proves clock updates can occur in a loop at this site; it does not establish its relation to animation publication or imply one update per rendered frame.

No direct CALL reference was found for publication wrapper 0x6A0740 in the code-section byte search. This does not mean it is unused: indirect calls/tables and jumps must be investigated. A definitive global scheduler ordering is still open. No viewer behavior changed.

## Next practical step

We now have enough verified default-state arithmetic to build a separately tested clock adapter, but it must not claim game scheduling parity. Resolve indirect ownership/call sites of 0x6A0740 and identify the relevant active loop, or use a targeted read-only capture of wrapper order plus the owner prefix if static tracing is inconclusive. Preserve optional mode settings rather than baking the 100 ms default into all paths.
