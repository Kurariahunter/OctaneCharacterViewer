# Configuration to transition activation — 2026-10-21

## Verified duration source

Preferred VA770150 is an activation caller. Its77017E..7701C9 instruction window obtains the controller's selected0x40-byte configuration row through76D1A0/76CC50. It reads the signed integer at row+24 and float at row+28, converts the integer to float and multiplies by the executable constant at1B2AC60:0.03333333507180214 (float32 approximately1/30). This is not a milliseconds-to-seconds conversion.

It passes the converted duration and separate float parameter to76CD90, which uses controller+64 and activates a0-to-1 TransitionProcessor through52D9B0. Native configuration parser77CEF0 identifies row+24/+28 as `Transition` fields. The earlier BlendIn(+14/+18) and BlendOut(+1C/+20) fields feed separate +60 paths; they should not be conflated with this transition fade.

`test_transition_configuration.py` executes the original instruction window, native row getters,76CD90 and52D9B0 on a synthetic pointer graph. All14 cases pass, including negative/zero values,3/6/30 units and an integer larger than float32's exact integer range. Two curve parameters are preserved independently. Three units produce0.10000000894069672 seconds, exactly the duration in the earlier live producer snapshot. This arithmetic agreement alone does not establish which historical row activated that live object.

The missing-row fallback in this window is integer-equivalent -1 and parameter1 before duration scaling. Negative values are preserved in the native tests; no universal replacement/default duration has been invented.

## Live ownership check

Read-only bridge revalidated PID104600, module MZ, controller+30 factor alias and controller+64 producer alias. Current handle0AE100E0 selects row0 at0AD4ACC0, whose Transition fields are -1 and1. This differs from the earlier producer's retained0.1-second setup. These snapshots are not synchronized to activation; a current configuration cannot be treated as proof of an earlier activation's arguments.

Evidence: `ElsaSceneResearch/ControllerState/live-transition-configuration-row.json`. Native tests: `transition-configuration-native-validation.json`; instruction evidence: `transition-activation-callers.txt` in the same directory.

## Reset boundary

The full activation caller also touches its AnimCurveControlProcessor and controller state+3C. That controller state is separate from each final scalar blender's previous output/fade/fade-bypass flag. Inspection of contributor registration5440C0 shows insertion/sorting and no explicit scalar fade reset in that routine. This does not establish that some broader registration/activation path never resets blending.

The scalar fade-bypass flag lifecycle remains unresolved. The viewer still uses its explicit full-weight single-clip setup. Do not reset every scalar state merely because an actor selects a new clip, or enable automatic game-like transitions based solely on the14 configuration cases.

Next: identify the final blender state reset writer and connect the activation-time configuration to the same controller. Existing bridge/static evidence should be used before requesting any new targeted execution capture. No additional user capture is required for the numerical configuration conversion demonstrated here.
