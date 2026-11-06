# Native packed matrix checkpoint — 2026-10-24

PC registry string ProcessorNode::DilationToMatrix4x4VariantProcessor at 0x01B30FBC registers factory 0x004F7DA0. Factory allocation reaches constructor 0x004DEDB0, which installs vtable 0x01B2F544. Its Compute slot +0x40 is 0x004DEE10. Compute reads the input Dilation payload through 0x0048D2B0, calls numerical converter 0x0048D9E0, then copies 12 floats into the output payload at +0x40.

The packed affine layout is three 3-component basis vectors followed by translation. The column convention used by the fixture is reshape(4,3).T with homogeneous row [0,0,0,1]. No translation or rotation correction is applied.

48 generated inputs with nonzero rotations/translations and positive uniform scales, plus 12 eyelid world outputs, were compared with original PC Transform-compose/point operations. All 60 passed, maximum component difference 2.384185791015625e-7. The report preserves inputs and packed outputs. This check was performed before replacing the fixture matrix generation with the direct native converter.

The fixture now exports native_pc_packed_affine and uses this original PC conversion directly for the four eyelid matrices. All 12 source binding/point-roundtrip checks still pass.

Wii U named evidence: VariantProcessor<Dilation3d,XfrmTransMat>::Compute at 0x021D67D0 calls Types::AugMat4x3::Dilation(Dilation3d) at 0x021484AC and assignment at 0x0214BF98. Complete byte-covered disassemblies are archived. This identifies a corresponding packed affine conversion path; direct linkage of that templated type to the serialized processor alias and numerical Wii U execution have not been independently established. Generic PowerPC disassembly has paired-single limitations.

Scope: original PC numerical validation on the bounded Wii U source fixture; no full actor scheduling, full palette, weighted mesh preview, or live Wii U parity claim. Production viewer unchanged.

Reproduce from project root:
```
python WiiUResearch/AnimationViewerResearch/validate_dilation_matrix_pc_native.py
python WiiUResearch/AnimationViewerResearch/evaluate_wiiu_head_fixture.py
python WiiUResearch/AnimationViewerResearch/validate_eyelid_skin_binding.py
```

Next: build an explicitly partial, source-bound mesh diagnostic for these eyelid influences, preserving the rest of the mesh at bind pose. Do not confuse that diagnostic with full character animation playback.
