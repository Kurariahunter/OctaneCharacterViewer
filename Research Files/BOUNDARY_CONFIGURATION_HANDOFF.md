# Boundary configuration application

Native controller setup at preferred 0x774360 obtains the curve state through 0x19368D0 (controller+0x50), then the selected 0x40-byte configuration row through 0x76D1A0. Existing default-row research established boundary byte row+0x3C = 0x58.

The setup copies row+0x3C to state+0x62 at 0x77442E, calls native range recomputation 0x525830, ORs state+0x62 with 0xA0 at 0x774436, and recomputes the range again. Therefore:

- Default row byte 0x58 becomes applied byte 0xF8.
- Explicit row byte 0x0E becomes applied byte 0xAE.

These values match both boundary bytes in the recent live capture. This explains their construction, but does not assign live pointers to a selected character/profile merely from matching flags.

`ElsaSceneResearch/validate_curve_boundary_setup.py` executes original setup window 0x774427..0x774443, including two complete calls to original 0x525830, for six cases (two row bytes, three finite ranges). All pass applied-byte and recomputed-range checks. Prebuilt state/row inputs skip earlier getter/initialization steps. The adjacent state byte +0x63 remains 3 during this window; starting evaluation requires separate activation behavior, already visible in 0x4969C0 which clears it and refreshes cached clock when resuming a frozen state.

Source evidence now connects the selected profiles' absent Layers/default row configuration to applied 0xF8 for this setup path. It does not make the existing 0x0E cyclic adapter appropriate for all profiles. The next implementation must support 0xF8 endpoint/stop semantics and explicit activation, then validate high-bit range behavior and 0xAE cyclic semantics where explicitly configured.

Saved research: ControllerState/curve-boundary-setup-validation.json and curve_boundary_configuration.txt. No renderer behavior changed. Do not label any current fixture as full-game scheduler parity.
