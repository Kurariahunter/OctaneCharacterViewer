# Scalar construction and channel binding assignment — 2026-10-21

Found a concrete assignment path for the observed composite field and default-network pointer.

## Constructor initialization

Original window533747..533770 initializes processor+18 to0000FFFF, +1C to null, +30 output pointer to null and +34 saved fade to0. The native test begins with nonzero poisoned memory and verifies these writes. Thus this constructor clears the bypass bit; it does not mark a first frame by setting it.

The Float-specific construction path calls this base constructor at4FCB37 and assigns Float-blender vtable1B2B8DC at4FCB3C. The binding loop's Float type branch at50033D..50036B rejoins the shared assignment block50042F. The test isolates that shared block rather than emulating the entire factory/loader.

## Binding assignment

500433 calls525400 to bind the output reference. Then50043B..50044C assigns the default-network reference through450900 and writes BP to processor+18 at500448 using a **16-bit store**. This replaces the channel index and preserves the high16 bits, including bypass. It does not write the saved fade or output scalar.

Six native binding tests cover indices33/39/FFFF with bypass both set/clear. All preserve high bits, fade0.25 and output7 while replacing the default reference. Reference counts update from3 to2 on the old reference and3 to4 on the new one. The test uses explicit x86 Windows InterlockedIncrement/Decrement import shims; no game call is replaced. Freeing/allocator paths and the earlier output setter are excluded.

Evidence: `ElsaSceneResearch/ControllerState/scalar-binding-assignment-validation.json` and `scalar-binding-assignment-disassembly.txt`.

## Viewer state change

`native_scalar_state.ScalarStates.seed` now defaults to bypass=False and saved fade0, matching the verified constructor fields. Seeded output0 is still an explicit preview fixture because the constructor only sets an output pointer to null. Existing state remains keyed per control and is not reset when a source changes. Current full-weight preview outputs remain source values; no manual pose adjustment was introduced.

The wrapper still reproduces306 recorded game values, and a new unseeded state with output0/target10/factor0.25 returns2.5 through the original native blender rather than bypassing the fade. Captured states explicitly override defaults during replay.

## Remaining boundary

This establishes constructor clearing and channel-binding preservation. It does not identify every possible setter that could turn bypass on later, nor prove full actor activation scheduling. For the captured306 evaluations the bit was clear, consistent with this construction path. Do not keep treating its unknown nonzero-mode setter as a demonstrated blocker for the observed clear-bit path.

Next useful check is activation-time configuration and fade production for one source change, using the known controller and constructor/binding rules. That would close a more relevant observed-path boundary than another broad instruction-pattern search.
