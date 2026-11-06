# Hips and leg IK research

TransformDilationWithDilation: factory0x4d70c0 -> constructor0x4b74e0 -> vtable0x1b2ca74 -> execute0x4d7440. Original code independently emulated in100 deterministic tests including rotation, translation and positive uniform scale. Moutput=Mconverter@Minput. Max error9.43e-7. See dilation-native-validation.json.

Hip output410 default rotation matches skin bind within3.43e-8. Explicit skin-pivot reconciliation0.0007962 units; no broad rotation correction. Active local hip channel is constant; passive varies by matrix-entry span0.04269. Clip-local constant hip orientation materially changes the passive pose even at first sample.

Legs require IK2BRPLengthSquashZConstraint processors408/412. Four OutputRotation[n]/OutputScale[n] fields were missed by old producer discovery. Fixed recognition; unsupported IK now fails explicitly rather than using stored defaults. Four output regression checks pass. Runtime located at0x53b620, factory0x54b880, vtable0x1b343ec; not decoded. See leg-ik-research.json for17 operands per leg. Additional undecoded basis/position processors remain in leg dependencies.

Hip preview is a diagnostic, not a better complete idle. Visible passive skirt/feet swing away from the floor because hip pose is applied without leg IK and dress corrections. Do not use as finished animation. Floor grid intentionally exposes this. Previous body/torso previews preserved. No invented knee/ankle/foot curves. Source mesh/texture data remain Editor research dependencies. No production importer changes.

Unity isolated validation passed: finite skinned vertices, local sample error<=2.99e-7, bind error2.58e-7, saved Animator movement and unchanged unrelated local transforms. Render inspected: confirms missing leg compensation, not successful foot planting.
