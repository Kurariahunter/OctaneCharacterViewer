# Elsa animation investigation — latest results

The supplied executable matches the earlier analyzed build (SHA256 in executable-findings.json). Original game files and Unity scripts were not modified.

## Progress
The on-disk interleaved command reader previously mistook 0x11 for a descriptor count of 17. Interpreting the low nibble as the count and preserving 0x10 separately makes the command streams land on their declared boundaries. This is corroborated structural evidence across the samples, not a confirmed meaning for the flag. The traced PC runtime loop uses packed port/count words, so the on-disk-to-runtime conversion still needs to be located.

After preserving that flag and using the traced eight-byte rotation-family records, 22 of 30 motion samples pass the supported structural and continuity checks. One more parses but has a large continuity warning; seven remain unsupported. Five of the six idle samples pass those checks. elsa_bm_idle_specific02 has a 2353-quantization-unit discontinuity and must not be treated as validated.

Active idle: 4.2 seconds, 28 curve blocks, 50 registers.
Passive idle: approximately 6.166667 seconds, 18 curve blocks, 45 registers.

Six static facial samples are excluded by the animated-header reader; that does not mean the assets are damaged. The remaining unsupported attack starts at command 0x0019, payload offset 0xAC.

## Independent native curve check
The original 0x522CF0 routine was run in isolated x86 emulation on active/passive idle curve blocks. All 276 sampled curve/component-group cases returned finite outputs. Python interpolation differs by up to 0.02203721 raw units (passive idle curve 10). Successful evaluation does not establish engine-version compatibility for every operation or validate the whole animation. The native output should serve as the reference while interpolation is refined.

## What remains
Resolve the 0x10 record flag and on-disk-to-runtime command conversion; validate static operands and commands; map Elsa's ports to her procedural rig; evaluate that graph and its base/additive composition. Then build a small visually reviewable animation test. No full-body playback claim is made.

## Files
- compare_idle_curves.py: reproducible research comparison, uses the existing Yoda curve source.
- elsa_timed_curve_decoder_snapshot.py: exact generated research decoder variant, importable without the missing helper.
- timed-curve-comparison.json: per-motion command/curve results and failure diagnostics.
- validate_elsa_native_curves.py / elsa-native-curve-validation.json: isolated native reference sampling and numerical differences.
- command-loop-disassembly.txt / interpreter-disassembly.txt: supporting PC machine-code excerpts.

Existing earlier findings are chronological; this report supersedes the previous 3-of-30 and 12-of-30 counts.
