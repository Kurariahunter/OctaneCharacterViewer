# Engine clock modes: 2026-10-19

Continues ENGINE_CLOCK_WRITER_HANDOFF.md. Preferred addresses and EXE identity are unchanged. No viewer pose or timing behavior was changed.

## Verified discrete configuration

Original function 0x6781A0 translates a selection into owner+0x28 mode and, when applicable, owner+0x30 shift:

| Selection | Mode | Shift | Effective delta from already capped uint32 input d |
|---|---|---|---|
| 0 | 0 | unchanged | 0, except pending one-shot |
| 1 | 1 | 4 | max(1, d >> 4) |
| 2 | 1 | 3 | max(1, d >> 3) |
| 3 | 1 | 2 | max(1, d >> 2) |
| 4 | 1 | 1 | max(1, d >> 1) |
| 5 | 2 | 1 | uint32(d << 1) |
| 6 | 2 | 2 | uint32(d << 2) |
| 7 | 2 | 3 | uint32(d << 3) |
| 8 | 2 | 4 | uint32(d << 4) |
| unsigned values >8 | 3 | unchanged | d |

Corresponding float scale getter 0x678330 returns 0, 1/16, 1/8, 1/4, 1/2, 2, 4, 8, 16 for selections 0..8, otherwise 1. These are code meanings, not recovered enum names.

Mode 0 checks byte owner+0x50. If set, it emits owner+0x34 milliseconds once and clears that byte. Mode 4 uses owner+0x44 as float multiplier, truncates toward zero, and substitutes 1 if the integer result is zero. Tests cover a positive 0.5 multiplier; negative/nonfinite/overflow policy is not established here. Modes 1 and 4 can advance by 1 ms even with a zero input; do not model all these modes as delta*scale in floating-point seconds.

The cap is applied before this discrete selection in 0x67AFF0. The native tests supply the already capped value directly, including 100 ms; they do not execute or test the cap itself.

## Validation

`validate_pc_engine_clock_modes.py` runs the complete original configuration function for ten selections and the original 0x67B0E6..0x67B1B6 mode/accumulation window for 48 cases: modes 0..4, shifts 1/4, input deltas 0/1/16/100, and both one-shot states for mode 0. All pass. Incoming dispatch registers, x87 constant, stack and capped EDI are fixture inputs. This is separate from the 16 accumulation-tail cases from the previous step.

Transition smoothing, controlled by owner+0x51, takes an earlier branch and remains outside these tests. Mode configuration 0x6788C0 and transition helper 0x678860 show the current/target scale fields, but their complete lifecycle still needs validation. Active live mode and cap defaults have not been captured; do not infer them from selected test inputs.

## Scheduling evidence and limits

Verified wrapper 0x69F9A0 calls host bridge 0x496B00 with ECX=0x21AEED8, then calls 0x77C460 and tail-jumps to 0x6490B0. Direct-call byte references locate its candidate caller at 0x6A0743. That caller still needs function-boundary and control-flow inspection before claiming global update order.

Wrapper 0x133EE60 updates the owner at 0x22018F0 through 0x67AFF0. Other call sites include setup 0x1378D10, which decrements the token after updating, and a polling loop calling 0x67AFF0 at 0x67B8D8. Thus the token cannot safely be labeled a rendered-frame number.

Next: validate transition smoothing and inspect the caller around 0x6A0743 alongside update wrappers to establish the relevant evaluation order. A later targeted capture can confirm active settings if static analysis cannot establish them. No new capture is required yet.
