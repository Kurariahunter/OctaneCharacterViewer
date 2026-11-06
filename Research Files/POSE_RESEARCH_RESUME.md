# Pose research resumed — 2026-10-21

Return from window-mode experiments. Native baseline remains unadjusted. Existing live idle finger comparisons show compatible hand-relative poses but do not identify played clips or synchronized phase. Bridge status is expired (prior PID67612); game restarted during window experiments, so old object addresses cannot be reused without revalidation.

## Narrowed idle02 continuity warning
Audit audit_pc_idle_discontinuities.py verifies original-PC payloads. All three differ in hash from earlier downloaded archive; however, PC idle02 really does retain the 2353-quantization-unit warning. It must not be dismissed merely as wrong-source evidence.

The only >3-unit continuity warnings in the three PC specific idles are:
- idle02 curve23, register40, ~5.999949sec: Cntrl_Eye Transform translationX, port287/node344; native output span .0028421767.
- idle02 curve24, register41, ~.166629sec: Cntrl_Eye Transform translationY, same control; native output span .0023833457.

Original EXE scalar routine 522CF0 reproduces both boundary steps across +/-two quantized time ticks. This establishes native-compatible sampled eye-control values, not authored intent or rendered eye/whole-character parity. Neither flagged channel is a finger channel. Do not smooth them as a generic decoder repair. Idle01/03 maximum continuity metric remains3. Source assumptions updated with precise scope; pose sample arrays unchanged.

Report: ControllerState/pc-idle-discontinuity-audit.json, including original EXE/model/payload hashes, per-boundary native samples and exact channel references.

Next live step remains active source/clock identification and synchronized pose comparison. Requires a fresh bridge READY and relocation/identity validation after game restart; no need to repeat known scalar/operator/finger math checks. No new CE capture requested yet and no claim of visual improvement from this audit.
