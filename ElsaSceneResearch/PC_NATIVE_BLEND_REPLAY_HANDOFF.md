# Native blend replay: captured and controlled validation

2026-10-17. No Unity assets, original game files or live game memory changed.

## Result

The original blend executor at preferred-image VA0x4e35d0 now runs offline with synthetic cached nodes. It reproduces all109nonempty snapshots from ce_blendexec_20261017_204631_310307171.jsonl exactly numerically in the8float output. Controlled noncommuting rotations then distinguish the tested additive composition order. This establishes a bounded native blend adapter, not the missing BlendMethod loader-to-runtime link or a complete actor blending system.

## Captured replay

Executable SHA256 f76cfd67b5e7675543c7f6e38e7cf41ae0a02b520f8b2cba47d9e6d5ae6c3705.
Capture SHA256410b992654ecdd059f1a096d67cc793b40449070ab919263161e064bec0b38ed.

native_pc_blend_replay.py maps separate scratch memory in the existing hash-pinned x86 Unicorn image. It builds a processor, contribution table, per-contributor controllers/containers, verified getter vtables, cached input nodes, weight arrays, factor scalars and output stamp metadata.

Original input64byte prefixes, flags, priorities, weight values and factor values come from each captured contribution. The original slot/weight-index locations are compacted to slot0/weight0 in separate synthetic containers; high packed-word flags are retained. Node stamps match synthetic metadata to prevent lazy traversal into uncaptured upstream producers. The comparison type mask/expected globals are neutralized in the synthetic fixture. Thus upstream production/type discrimination is outside this replay; the numerical executor still runs original machine code.

The processor is configured for full replacement (high bit of processor+18 set), no default-network pose and no temporal fade. These processor settings were not captured by the logger. They are explicit fixture conditions that match this dataset; do not claim they were independently observed in the running game.

Output is initialized to identity, not the recorded result. The native executor must reach a sentinel return address within the instruction budget and produce finite output. Predicted output is then compared with the independently recorded output.

-109nonempty records:56single,48double,5triple contributors.
-Maximum output component difference0.0 across all109.
-11empty-table records excluded because original prior/default state was not captured. Identity initialization cannot justify an empty-table claim.
-Captured active flagged rotations remain near identity, so numerical equality here alone does not establish noncommuting rotation order.

## Controlled experiments

validate_pc_blend_controlled.py uses three mixed-axis base rotors, three mixed-axis delta rotors and weights0,0.25,0.5,1:36primary cases. Base has flag0 and weight1, delta has flag1 and tested weight; table is base first, delta second. Both have priority5; factor2c and factor30 are1; all scales are1. Base translation is[1,2,3]; delta translation[0.4,-0.3,0.2].

For this configuration the native result agrees with:

```text
weighted_delta = normalize((1-w) * identity_rotor + w * delta_rotor)
output_rotor = HamiltonMultiply(weighted_delta, base_rotor)
output_translation = base_translation + w * delta_translation
output_uniform_scale = 1
```

Quaternion order is explicit xyzw Hamilton algebra as implemented in probe_pc_blend_order.py. Primary deltas have positive w. Source quaternion-to-matrix conventions differ from an unqualified Unity convention; do not paste this product into Unity without the established basis conversion.

-36primary cases pass.
-Maximum quaternion component difference6.557839105081342e-8, considering q/-q equivalence.
-Maximum translation difference9.536743172944284e-8.
-The opposite product base*weighted_delta differs by as much as0.3951250731466883per quaternion component. This is a discriminating test, unlike near-identity captured deltas.

Two additional36-case diagnostics:

- Negating the input delta quaternion gives identical output orientation in these cases (maximum difference0.0). This supports sign-invariant treatment in the tested range, not every boundary around180degrees.
- Reversing contribution-table order gives different results: maximum difference0.41008807718753815relative to the base-first result. In this reversed two-record, equal-priority arrangement, the output rotor matches the base alone within2.885715488787355e-8. Thus flagged entries cannot simply be moved/reordered with an assumption that the same additive effect will survive.

These tests do not establish multiple additive-layer order, different priority groups, over/negative weights, arbitrary nonuniform scale, temporal fades, missing-base/default-network behavior, full loader mode transfer or actual clip ownership in live captures.

## What this enables next

We can now replay a bounded observed blend and distinguish a meaningful additive order under stated conditions. Next trace how the source track's normalized mode selects and orders its actual runtime contributors, including the correct executor for each control type. Then use the native adapter on the verified run lean controls in a separate experimental export. Do not present this as proof that the currently omitted run lean track has been identified in the live capture; its active identity was not recorded.

## Reproduce

From F:/DisneyInfinityPortalTest/ElsaSceneResearch, using the configured Python environment and pinned executable:

```powershell
python validate_pc_blend_capture.py
python validate_pc_blend_controlled.py
```

Files:

- native_pc_blend_replay.py — bounded original executor adapter.
- validate_pc_blend_capture.py — live numeric fixtures to predicted output comparison.
- pc-native-blend-capture-replay.json — full per-record predictions and exclusions.
- probe_pc_blend_order.py — explicit xyzw quaternion math and initial probe.
- pc-native-blend-controlled-probe.json — initial four-weight probe.
- validate_pc_blend_controlled.py — primary and order/sign diagnostics.
- pc-native-blend-controlled-validation.json — full controlled results.

Mirrored in C:/Users/Kurar/Disney Reloaded/Tools/ExecutableResearch/DressResearch.
