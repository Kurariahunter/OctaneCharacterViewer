# Child clock callback — 2026-10-19

Continues CLOCK_TRANSITION_HANDOFF.md with the same hash-pinned PC executable. No viewer behavior changed.

## Callback identity and ownership

0x67AC00 traverses a container at parent+0x58. For each entry, it passes the pointer stored at entry+0x0C as ECX to the direct call 0x679000. This is a concrete child-clock updater, not an unresolved virtual user callback. Its four stack arguments are forwarded from the traversal's own arguments: raw delta, capped delta, and two additional values. The parent caller supplies these before updating its own accumulation fields.

0x679000 accesses a compact child clock layout different from the parent:

| Child offset | Meaning established by code |
|---|---|
| +0x00 | Effective integer delta |
| +0x04 / +0x08 | Previous/current accumulated integer time |
| +0x0C | Effective delta seconds |
| +0x10 / +0x14 | Previous/current float seconds |
| +0x18 / +0x1C | Selected/previous mode |
| +0x20 | Shift |
| +0x24 | One-shot delta |
| +0x28 / +0x2C / +0x30 | Smoothing parameter/current scale/target scale |
| +0x34 | Expiry/countdown value; not exercised here |
| +0x38 | Custom multiplier |
| +0x3C / +0x3D | One-shot/transition flags |

The child has corresponding discrete and smoothing paths. Its smoothing branch also retains the existing effective integer delta. The earlier hypothesis that this callback might compute the parent's effective delta is not supported by its instruction stream: ordinary state writes are child-relative; there is no parent pointer write. It reads parent global 0x220190C in its countdown path. Container removal after the call is separate and not tested here.

## Native tests

`validate_pc_child_clock.py` executes the entire original function 0x679000 for 30 cases: five modes, three raw/capped delta pairs (0/0, 16/16, 100/50), and smoothing disabled/enabled. A synthetic child begins with effective delta 17 ms and accumulated time 1000 ms. The expiry field is zero.

Every case passes expected discrete delta or retained transition delta, accumulated time, and a Unicorn memory-write hook checking that every write lies within the 0x40-byte child or the call stack. No parent writes occur in these fixtures. The test does not execute traversal/removal, exercise expiry, or prove live pointers cannot alias. It does execute full native child-update entry through return, with no substituted callees.

## Consequence and next step

The parent smoothing result from the preceding research stands: its post-callback branch does not recompute parent+0x10. Do not invent a delta-times-smoothed-scale implementation. We still need the transition setup/lifecycle and active clock state to explain how this behavior is used by the game.

Next inspect writes/configuration of parent+0x10 and the transition-entry methods, then establish the relationship between clock-update wrapper 0x133EE60 and publication wrapper 0x6A0740. The callback ambiguity is resolved without requiring another user capture. Viewer timing integration remains pending those checks.

Artifacts: child-clock-validation.json, child_clock_update.txt, child_clock_traversal.txt, and the validation script in the research root.
