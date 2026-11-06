# Default layer configuration verified

2026-10-19

Loader 0x787200 reads `Layers` (global string 0x2120644) and `Channels` (0x212064C). In the inspected branch, zero layer children leads to a request for one configuration row at owner +0x20. Nonzero children lead to one 0x40-byte row per layer, then explicit row parsing through 0x77CEF0. The explicit row iteration is statically traced; the complete outer loader is not executed here.

Complete native row constructor 0x77A600 was executed for 0, 1, 2 and 7 rows, with guard checks. The original absent/empty Layers instruction window 0x787329..0x787342 was also executed with preallocated storage and original callees: both produce exactly one native-default row. No call-result stubs or heap allocations were used.

Fresh rows contain four empty string members at +0/+4/+8/+0xC (Filter at +8, Mirror at +0xC). Exact numeric defaults are in layer-config-default-validation.json; unidentified field meanings are not inferred. The row constructor sets flags +0x3C to 0x58 and leaves final padding bytes untouched. Together with the earlier resolver tests, empty Filter names select null and the blend consumer's null Filter path uses coefficient 1. This closes the default-filter question for the inspected no-Layers file-loading path; it does not reconstruct the runtime scheduler or every configuration mutation path.

The four supported viewer profiles now include source_filter_configuration metadata, produced by pc_preview_filter_configuration.py. STANCE, STANCE_PASSIVE, WALKRUN have one default row, empty Filter/Mirror names, and no selected Filter. It pins the known BENT SHA256 and checks the assignment audit before recording this claim. The helper validates all four profiles; evaluate_native_clip.py parses successfully. No pose arithmetic or motion output was changed and no full preview bake was rerun for this metadata-only addition.

Next identify the controller/file/layer association, clip phase and active scalar weights together in a live state, or trace the scheduler that supplies them. The known source default is no longer a reason to add an arbitrary upper-body mask. Explicit layers and concurrent controllers remain distinct from the selected entry's default row.
