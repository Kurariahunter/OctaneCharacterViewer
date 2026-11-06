# PC dress-anchor and orientation checkpoint

Generated 2026-10-17 from octane_20261017_151848_1792264728047355700.json. All execution is offline, hash-pinned to the installed PC EXE. Capture and production Unity assets unchanged.

## New tools

- evaluate_pc_dress_anchors.py: bounded native recomposition of descendants of the traced thigh aggregates. Uses the original ConcatenateChainDilation, ConcatenateChainInverseDilation, InvertDilation and ConcatenateDilationTransform routines. The observed one-input VariantAdapter is copied as an identity; unsupported descendant operations or multi-input variants fail. Captured branches outside the thigh dependency closure remain explicit external inputs.
- native_pc_dress_math.py: PC-isolated original difference, inverse-vector and Aim fixtures. No old source-model or clip imports.
- validate_pc_dress_orientation.py: verifies installed PC source connectivity from DynamicChain positions through difference, inverse-vector and Aim, then compares generated local rotations with captured cached orientations.
- Generate PC Dress Research.cmd: regenerates both JSON reports using the existing capture. Not a live capture launcher and needs no administrator rights.

These are research adapters bound to this capture's runtime node addresses. They are not a general importer or original-animation exporter.

## Findings

24 downstream nodes recomposed per sampled graph; 60 samples per side. Anchor raw Transform maximum component errors 0.03788838 and 0.00336665. 55/60 and 56/60 anchor results are below 0.00001 component error. Remaining branch values are captured, not decoded animation inputs.

Local operator checks: 567/600 chain Dilation, 119/120 mixed normal/inverse Dilation, 239/240 Dilation+Transform, 237/240 inverse Dilation and 240/240 observed identity variant checks are below 0.00001. Do not claim all anchor paths exact: non-atomic captures and unresolved discrepancies remain.

PC source connectivity:
- DynamicChain 550, AnchorToWorld 643, Position outputs 696/701 -> difference -> inverse-vector processor 430 -> Aim processor 429 -> rotor 689.
- DynamicChain 551, AnchorToWorld 649, Position outputs 712/717 -> difference -> inverse-vector processor 440 -> Aim processor 439 -> rotor 705.

Using captured particle positions and captured anchor transforms, original native difference/inverse/Aim reproduces captured cached rotations with zero measured angular difference in all 120 comparisons. This is normalized quaternion angular agreement at numerical precision, not a claim of bit-identical payloads.

Substituting partially recomposed anchors yields maximum angular differences of 2.8924146 and 4.0913034 degrees. Thus the orientation stage is strongly validated, while the complete thigh-to-anchor path still needs reconciliation of sample timing and external inputs.

## Verification and limits

Python compilation passed. Failure checks reject unknown dependent operators and unvalidated multi-input variants. Report generation passed; 120 mapped anchor rows and 120 orientation rows. Native PC solver replay remains in its separate report.

Particle positions are captured inputs. No temporal simulation, velocity recovery, clip-channel reconstruction, skinning or Unity coordinate conversion has been added in this checkpoint. Next: obtain a synchronized PC input/state baseline, reconcile anchor outliers, then run temporal DynamicChain stepping with the correct PC state and parameters. Do not merge the older 13/4 solver family into this pipeline.
