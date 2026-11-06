# EXE checkpoint: normalized parameters and remaining viewer dependencies

2026-10-18. All addresses are preferred VAs for the SHA-pinned PC executable, base 0x400000. Live ASLR addresses are module base + RVA, not these raw VAs.

## Verified native behavior

### Normalized parameter accessor — 0x59d3c0

For the tested finite inputs, returns 1 when field +0x18 is zero; otherwise clamps (field +0x10 - field +0x14) / field +0x18 to [0,1]. Actual single-precision intermediate behavior is exercised, not inferred from a Python formula alone. Signed zero and negative denominators were tested. This was previously called an expression-backed getter; that wording was overly general. It is a concrete normalized scalar accessor. The three raw offsets do not prove their owning runtime parameter's name or units.

### Track weight — 0x59d500

When the pointer at track +0x0C is non-null, delegates directly to that normalized accessor. It does NOT multiply the result by the constant field +0x10. When the pointer is null it returns the constant field as-is, including values outside [0,1].

### Setter — 0x59d9d0

Stores field10 = field14 + field18 * clamp01(input). Complete routine executed on null callback pointer fixtures. The optional callback/notification path is not exercised or stubbed.

### Clip-time mapping — instruction window 0x59fc2e..0x59fc5f

If source pointer at enclosing object +0x24 is present, it reads that normalized scalar, calls original range getters on object +0x28 and replaces the local clip time with range34 + normalized * (range38-range34). The getter at 0x503c10 returns range38-range34; 0x76bef0 returns range34. When the source pointer is null, existing local time is retained. This is an original instruction window, not the complete clip evaluator. No callback/call-result stubs were used in this window.

144 finite field combinations tested through both the accessor and track delegation; 72 setter cases; 30 time-remap cases, one null-source preservation case, and five constant getter cases. All passed. Evidence: pc-normalized-parameter-validation.json, validate_pc_normalized_parameter.py and disassembly/byte hashes in pc-normalized-parameter-research-manifest.json.

## Static source connections

Direct-call candidates: 0x59dc5c (group selection) and 0x59fc35 (clip-time remapping). The track getter tail-jumps to the accessor. The native group-selection code compares the normalized result with key intervals; this supports investigating actual Speed/Direction normalization rather than interpreting BENT motion-rate metadata as time multipliers.

Parser 0x77cef0 was previously located by the Filter property. Further disassembly shows one 0x40-byte configuration record with Filter at +8, Mirror at +0x0C, WeightWhenDone at +0x10, BlendIn at +0x14, BlendOut at +0x1C, Transition handling and Control handling. Caller 0x78742a indexes records with a 0x40 stride. These are static field/write observations, not proof of resolved filter coefficients or complete live scheduling. Control parsing writes values at +0x34/+0x38; relation to the runtime clip range is a candidate until object transfer/ownership is traced. A string match CachedMaskFilter is only a lead, not confirmed animation mask code.

## The skipped forearm channels

pc-forearm-external-channel-audit.json covers both idles and both walk/run lower/upper clips, at five phases each.

- 364 = Anchor|Cntrl_ForearmAttach_Left|Transform, External=1; producer 185, DilationTranslationOrientationConnection, input 365.
- 382 = corresponding Right attachment, External=1; producer 193, input 383.
- Idle ports 405/406 target those outputs with zero translation/identity orientation at the sampled phases. Walk/run lower and upper clips do not directly target these four nodes in the sampled records.

Thus these are not currently demonstrated missing animated index-finger curves. The sampled identity data do not establish generic external-channel versus processor precedence. No override, reparent, or visual correction was added.

## What we still need from the EXE

1. **Parameter binding and update:** trace construction/registration of normalized objects and links from track +0x0C, clip +0x24 and group +0x40 to identified actor Speed/Direction/weight values. The math is known; live ownership and update order are not. Do not insert guessed parameter values into the viewer.
2. **Filter resolution/application:** follow the parsed filter-name record to the resolved coefficient/bit-mask object and the control/channel weights used by clip-buffer blending. Filter string loading alone is insufficient.
3. **External channel precedence/defaults:** determine how clip buffers initialize controls, select component masks and interact with producer graphs. This is needed before applying currently skipped computed-output channels or dropping the passive-idle initialization fixture.
4. **Actor scheduling/dynamics:** retain exact active layers, local times, root motion, gravity/collision scene and feedback state. Numerically correct isolated functions are not an entire engine.

## Next live capture, once ownership is identified

Read-only, hotkey-armed and bounded. Identify the Elsa actor first, then capture in the same update/frame: actor/network identity, source clip identity and local time, Speed/Direction, normalized-source fields, effective track weight, resolved filter identity/weights, final palette and dynamic chain state. Getter/loader calls without actor association are not enough. Loader-only hooks may fire before gameplay; use a verified per-frame evaluation point. No new Cheat Engine run is requested yet: the parameter ownership and filter target must be narrowed first.

## Viewer status

Current previews remain unchanged. Selected source profiles still evaluate partial PC Elsa graph paths with recorded fixtures and 46/16 coverage. The new math is research-verified but intentionally not wired to arbitrary presumed live values. This checkpoint advances the loader/parameter reconstruction rather than changing motion by guesswork.
